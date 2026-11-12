import sys

MARKER = "- **CURRENT STATE"


def main(argv):
    if len(argv) != 4:
        print("usage: prepend_state.py <state file in> <block file> <state file out>", file=sys.stderr)
        return 2
    src, block, out = argv[1], argv[2], argv[3]
    try:
        with open(src, encoding="utf-8", newline="") as f:
            lines = f.read().split("\n")
        with open(block, encoding="utf-8", newline="") as f:
            add = f.read().rstrip("\r\n").split("\n")
    except OSError as e:
        print("prepend_state: cannot read " + str(e.filename) + ": " + e.strerror, file=sys.stderr)
        return 1
    k = next((i for i, line in enumerate(lines) if line.startswith(MARKER)), None)
    if k is None:
        print("prepend_state: no line starting with '" + MARKER + "' in " + src + "; nothing written", file=sys.stderr)
        return 1
    lines[k:k] = add
    try:
        with open(out, "w", encoding="utf-8", newline="") as f:
            f.write("\n".join(lines))
    except OSError as e:
        print("prepend_state: cannot write " + str(e.filename) + ": " + e.strerror, file=sys.stderr)
        return 1
    print("inserted", len(add), "lines at line", k + 1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
