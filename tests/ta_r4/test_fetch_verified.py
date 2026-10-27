"""W2a T1: verified download helper (md5/sha256/size/magic checked before the rename)."""
from __future__ import annotations

import gzip
import hashlib
import http.server
import io
import ssl
import subprocess
import tarfile
import threading
from pathlib import Path

import pytest

from ta_r4 import fetch_verified as fv


def _tgz_bytes():
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        data = b"hello\n"
        ti = tarfile.TarInfo("top/a.txt")
        ti.size = len(data)
        tf.addfile(ti, io.BytesIO(data))
    return buf.getvalue()


TGZ = _tgz_bytes()
GZ_NOT_TAR = gzip.compress(b"just text, not a tar archive\n" * 50)
NPZ = b"PK\x03\x04" + b"\x00" * 60
HTML = b"<!DOCTYPE html><html><body>Please log in</body></html>\n"


@pytest.fixture(scope="module")
def server(tmp_path_factory):
    d = tmp_path_factory.mktemp("srv")
    (d / "www").mkdir()
    (d / "www" / "f.tgz").write_bytes(TGZ)
    (d / "www" / "plain.gz").write_bytes(GZ_NOT_TAR)
    (d / "www" / "page.tgz").write_bytes(HTML)
    (d / "www" / "t.npz").write_bytes(NPZ)
    key, crt = d / "key.pem", d / "crt.pem"
    subprocess.run(
        ["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", str(key), "-out", str(crt),
         "-days", "1", "-subj", "/CN=localhost", "-addext", "subjectAltName=DNS:localhost"],
        check=True, capture_output=True,
    )
    www = str(d / "www")

    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=www, **k)

        def log_message(self, *a):
            pass

    httpd = http.server.HTTPServer(("localhost", 0), H)
    sctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    sctx.load_cert_chain(str(crt), str(key))
    httpd.socket = sctx.wrap_socket(httpd.socket, server_side=True)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    cctx = ssl.create_default_context(cafile=str(crt))
    yield f"https://localhost:{httpd.server_address[1]}", cctx
    httpd.shutdown()


def _root(tmp_path):
    r = tmp_path / "downloads"
    r.mkdir()
    return r


def test_good_tgz_verified_and_renamed(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    md5 = hashlib.md5(TGZ).hexdigest()
    out = fv.fetch_verified(f"{base}/f.tgz?download=1", root / "src", md5=md5, size=len(TGZ),
                            magic=("gzip", "tar"), downloads_root=root, ssl_context=ctx)
    p = Path(out["path"])
    assert p == (root / "src" / "f.tgz").resolve()
    assert p.read_bytes() == TGZ
    assert out["md5"] == md5
    assert out["sha256"] == hashlib.sha256(TGZ).hexdigest()
    assert out["size"] == len(TGZ)
    assert out["magic"] == ["gzip", "tar"]
    assert sorted(x.name for x in (root / "src").iterdir()) == ["f.tgz"]


def test_size_mismatch_raises_and_deletes_part(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(fv.VerificationError, match="size"):
        fv.fetch_verified(f"{base}/f.tgz", root / "src", size=len(TGZ) + 1,
                          downloads_root=root, ssl_context=ctx)
    assert list((root / "src").iterdir()) == []


def test_md5_mismatch_raises(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(fv.VerificationError, match="md5"):
        fv.fetch_verified(f"{base}/f.tgz", root / "src", md5="0" * 32, downloads_root=root, ssl_context=ctx)
    assert list((root / "src").iterdir()) == []


def test_sha256_mismatch_raises(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(fv.VerificationError, match="sha256"):
        fv.fetch_verified(f"{base}/f.tgz", root / "src", sha256="0" * 64, downloads_root=root, ssl_context=ctx)
    assert list((root / "src").iterdir()) == []


def test_html_body_with_200_fails_magic(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(fv.VerificationError, match="magic"):
        fv.fetch_verified(f"{base}/page.tgz", root / "src", downloads_root=root, ssl_context=ctx)
    assert list((root / "src").iterdir()) == []


def test_gzip_that_is_not_tar_fails_tar_check(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(fv.VerificationError, match="tar"):
        fv.fetch_verified(f"{base}/plain.gz", root / "src", magic=("gzip", "tar"),
                          downloads_root=root, ssl_context=ctx)
    assert list((root / "src").iterdir()) == []


def test_refuses_http_url(tmp_path):
    root = _root(tmp_path)
    with pytest.raises(ValueError, match="https"):
        fv.fetch_verified("http://localhost/f.tgz", root / "src", downloads_root=root)
    assert not (root / "src").exists()


def test_refuses_nonempty_dest(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    (root / "src").mkdir()
    (root / "src" / "other.txt").write_text("x")
    with pytest.raises(ValueError, match="not empty"):
        fv.fetch_verified(f"{base}/f.tgz", root / "src", downloads_root=root, ssl_context=ctx)
    assert sorted(x.name for x in (root / "src").iterdir()) == ["other.txt"]


def test_refuses_dest_outside_downloads_root(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    with pytest.raises(ValueError, match="under"):
        fv.fetch_verified(f"{base}/f.tgz", tmp_path / "elsewhere", downloads_root=root, ssl_context=ctx)
    assert not (tmp_path / "elsewhere").exists()


def test_no_shell_true_anywhere():
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(fv))
    for node in ast.walk(tree):
        if isinstance(node, ast.keyword) and node.arg == "shell":
            pytest.fail("shell= keyword used")


def test_manifest_row_appended(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    man = tmp_path / "downloads_sha256.tsv"
    out = fv.fetch_verified(f"{base}/f.tgz", root / "src", downloads_root=root, ssl_context=ctx)
    fv.append_manifest(man, "toy", f"{base}/f.tgz", out)
    fv.append_manifest(man, "toy", f"{base}/f.tgz", out)
    lines = man.read_text().splitlines()
    assert lines[0].split("\t") == ["source", "url", "file", "size_bytes", "md5", "sha256", "fetched_utc"]
    assert len(lines) == 3
    row = lines[1].split("\t")
    assert row[:6] == ["toy", f"{base}/f.tgz", "f.tgz", str(len(TGZ)), hashlib.md5(TGZ).hexdigest(),
                       hashlib.sha256(TGZ).hexdigest()]


def test_zip_magic_for_npz(server, tmp_path):
    base, ctx = server
    root = _root(tmp_path)
    out = fv.fetch_verified(f"{base}/t.npz", root / "a", magic=("zip",), downloads_root=root, ssl_context=ctx)
    assert Path(out["path"]).read_bytes() == NPZ
    with pytest.raises(fv.VerificationError, match="magic"):
        fv.fetch_verified(f"{base}/f.tgz", root / "b", magic=("zip",), downloads_root=root, ssl_context=ctx)
    assert list((root / "b").iterdir()) == []
