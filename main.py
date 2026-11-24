#!/usr/bin/env python3
"""Monday, Reviewed in One Line.

Writes a single-line, under-200-character review of my own Monday to
$MAKEFUN_OUTPUT_DIR/entry.txt (default /output), with no trailing newline.
Pure standard library only.
"""

import os
import sys
import tempfile

LINE = "Monday: my alarm showed up, my motivation ghosted me, and my coffee billed me for overtime."

OUTPUT_FILENAME = "entry.txt"
MAX_CHARS = 199


def main() -> int:
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output dir {out_dir!r}: {exc}", file=sys.stderr)
        return 1

    data = LINE.encode("utf-8")
    if not (1 <= len(LINE) <= MAX_CHARS):
        print(f"error: review is {len(LINE)} chars, must be 1-199", file=sys.stderr)
        return 1
    if "\n" in LINE or "\r" in LINE:
        print("error: review must be a single line", file=sys.stderr)
        return 1

    target = os.path.join(out_dir, OUTPUT_FILENAME)
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except OSError as exc:
        print(f"error: cannot write entry: {exc}", file=sys.stderr)
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        return 1

    # Read back and verify bytes, char count, and mode.
    try:
        with open(target, "rb") as fh:
            back = fh.read()
        st = os.stat(target)
    except OSError as exc:
        print(f"error: cannot read back entry: {exc}", file=sys.stderr)
        return 1
    if back != data:
        print("error: read-back bytes differ from written bytes", file=sys.stderr)
        return 1
    if len(back.decode("utf-8")) != len(LINE) or len(LINE) >= 200:
        print("error: char count verification failed", file=sys.stderr)
        return 1
    if back.endswith(b"\n"):
        print("error: entry has a trailing newline", file=sys.stderr)
        return 1
    if (st.st_mode & 0o777) != 0o644:
        print(f"error: entry mode is {oct(st.st_mode & 0o777)}, expected 0o644",
              file=sys.stderr)
        return 1
    print(f"wrote {target}: {len(LINE)} chars, {len(data)} bytes, mode 0644")
    return 0


if __name__ == "__main__":
    sys.exit(main())
