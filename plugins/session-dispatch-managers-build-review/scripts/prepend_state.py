import os
import sys
import tempfile

MARKER = "- **CURRENT STATE"


def fail(msg):
    print("prepend_state: " + msg, file=sys.stderr)
    return 1


def main(argv):
    if len(argv) != 4:
        print("usage: prepend_state.py <state file in> <block file> <state file out>", file=sys.stderr)
        return 2
    src, block, out = argv[1], argv[2], argv[3]
    try:
        with open(src, encoding="utf-8", newline="") as f:
            state = f.read()
        with open(block, encoding="utf-8-sig", newline="") as f:
            text = f.read()
    except OSError as e:
        return fail("cannot read " + str(e.filename) + ": " + e.strerror)
    except UnicodeDecodeError:
        return fail("state file and block file must be UTF-8; nothing written")
    text = text.replace("\r\n", "\n").rstrip("\n")
    if not text.strip():
        return fail("block file " + block + " is empty; nothing written")
    lines = state.split("\n")
    k = next((i for i, line in enumerate(lines) if line.startswith(MARKER)), None)
    if k is None:
        return fail("no line starting with '" + MARKER + "' in " + src + "; nothing written")
    tail = "\r" if "\r\n" in state else ""
    add = [line + tail for line in text.split("\n")]
    lines[k:k] = add
    tmp = None
    try:
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(out)), prefix=".prepend_state.")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))
        os.replace(tmp, out)
    except OSError as e:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
        return fail("cannot write " + str(e.filename or out) + ": " + e.strerror)
    print("inserted", len(add), "lines at line", k + 1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
