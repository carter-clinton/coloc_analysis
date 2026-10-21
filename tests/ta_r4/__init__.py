import sys as _sys
from pathlib import Path as _Path

# tests/ has no __init__.py, so pytest imports this dir as the top-level package
# `ta_r4`, which would shadow src/python/ta_r4. Put src/python first and extend
# __path__ so `ta_r4.<module>` also resolves to the source package.
_SRC = str(_Path(__file__).resolve().parents[2] / "src" / "python")
if _SRC not in _sys.path:
    _sys.path.insert(0, _SRC)
__path__ = __import__("pkgutil").extend_path(__path__, __name__)
