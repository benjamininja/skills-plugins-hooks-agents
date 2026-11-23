"""Every ADR file in docs/adr/ has a row in docs/adr/README.md."""
from pathlib import Path

ADR_DIR = Path(__file__).resolve().parent.parent / "docs" / "adr"


def test_every_adr_has_a_readme_row():
    readme = (ADR_DIR / "README.md").read_text(encoding="utf-8")
    rows = [line for line in readme.splitlines() if line.startswith("| [")]
    adrs = sorted(p.name for p in ADR_DIR.glob("[0-9][0-9][0-9][0-9]-*.md"))
    assert adrs, "no ADR files found"
    missing = [n for n in adrs if not any(f"]({n})" in row for row in rows)]
    assert not missing, f"ADR files with no README row: {missing}"
