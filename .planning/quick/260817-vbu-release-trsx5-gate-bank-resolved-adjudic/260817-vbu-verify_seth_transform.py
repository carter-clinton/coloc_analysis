#!/usr/bin/env python3
"""Independent replication of Seth's 6-step transform (2026-08-17 courier).

Steps, verbatim from his message:
  1. remove ** (bold) - 58 pairs
  2. remove single-asterisk *italic* pairs - 2 pairs
  3. remove all backticks
  4. remove the leading '- ' from each bullet
  5. insert a blank line before each de-bulleted item that follows
     non-blank content (paragraph re-flow)
  6. no trailing newline

Expected result: 9,695 bytes, 59 lines,
  md5    c19be8b2ad7cd6a45fee1d668d8a9cf9
  sha256 1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4
His byte accounting: asterisks -120 (1 literal survives), backticks -74,
bullet marks -26, blank lines +8 => net -212.
"""
import hashlib
import re
import sys

SRC = sys.argv[1]

src = open(SRC, "rb").read()
report = {}
report["src_bytes"] = len(src)
text = src.decode("utf-8")
report["src_ends_with_newline"] = text.endswith("\n")
report["src_asterisks"] = text.count("*")
report["src_backticks"] = text.count("`")

# Step 1: remove ** (bold)
bold_pairs = text.count("**")
t = text.replace("**", "")
report["bold_pairs_removed"] = bold_pairs

# Step 2: remove single-asterisk *italic* pairs (within a line)
italic_pairs = re.findall(r"\*[^*\n]+\*", t)
t = re.sub(r"\*([^*\n]+)\*", r"\1", t)
report["italic_pairs_removed"] = len(italic_pairs)
report["asterisks_surviving"] = t.count("*")

# Step 3: remove all backticks
report["backticks_removed"] = t.count("`")
t = t.replace("`", "")

# Steps 4 + 5: de-bullet, inserting a blank line before each de-bulleted
# item that follows non-blank content
out = []
debulleted = 0
blanks_inserted = 0
for line in t.split("\n"):
    if line.startswith("- "):
        if out and out[-1] != "":
            out.append("")
            blanks_inserted += 1
        out.append(line[2:])
        debulleted += 1
    else:
        out.append(line)
res = "\n".join(out)
report["bullets_debulleted"] = debulleted
report["blank_lines_inserted"] = blanks_inserted

# Step 6: no trailing newline
trailing_stripped = 0
while res.endswith("\n"):
    res = res[:-1]
    trailing_stripped += 1
report["trailing_newlines_stripped"] = trailing_stripped

data = res.encode("utf-8")
report["out_bytes"] = len(data)
report["out_lines"] = res.count("\n") + 1
report["out_md5"] = hashlib.md5(data).hexdigest()
report["out_sha256"] = hashlib.sha256(data).hexdigest()

for k, v in report.items():
    print(f"{k}: {v}")

EXP_MD5 = "c19be8b2ad7cd6a45fee1d668d8a9cf9"
EXP_SHA = "1ba83e4e633cd11c7f0896969cd6a419dada7b442365a5a0a3ea7307a342aab4"
print()
print("SIZE  :", "MATCH" if report["out_bytes"] == 9695 else "MISMATCH")
print("MD5   :", "MATCH" if report["out_md5"] == EXP_MD5 else "MISMATCH")
print("SHA256:", "MATCH" if report["out_sha256"] == EXP_SHA else "MISMATCH")
