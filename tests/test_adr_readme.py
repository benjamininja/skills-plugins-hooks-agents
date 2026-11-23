"""Every ADR file in docs/adr/ has a row in docs/adr/README.md."""
from pathlib import Path

ADR_DIR = Path(__file__).resolve().parent.parent / "docs" / "adr"


def test_every_adr_has_a_readme_row():
    readme = (ADR_DIR / "README.md").read_text(encoding="utf-8")
    first_cells = []
    for line in readme.splitlines():
        if line.startswith("| ["):
            first_cells.append(line.split("|")[1])
    adrs = sorted(p.name for p in ADR_DIR.glob("*.md") if p.name != "README.md")
    assert adrs, "no ADR files found"
    missing = [n for n in adrs if not any(f"]({n})" in c for c in first_cells)]
    assert not missing, f"ADR files with no README row: {missing}"
