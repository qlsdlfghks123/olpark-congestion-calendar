import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"
BUILD_OUTPUTS = {"forecast.json", "courses.json", "overlaps.json", "agency_overlaps.csv", "metrics.json",
                 "evidence_2025.json", "sources.json", "ics"}
TEXT_FILES = ["index.html", "agency.html", "evidence.html", "app.js", "app.css"]


def test_pages_exist():
    for f in TEXT_FILES:
        assert (SITE / f).exists(), f


def test_pages_reference_existing_data_files():
    refs = set()
    for f in TEXT_FILES:
        refs |= set(re.findall(r"data/([A-Za-z0-9_]+(?:\.json|\.csv)?)", (SITE / f).read_text(encoding="utf-8")))
    assert refs and refs <= BUILD_OUTPUTS, refs - BUILD_OUTPUTS


def test_no_emoji_or_em_dash():
    emoji = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
    for f in TEXT_FILES:
        t = (SITE / f).read_text(encoding="utf-8")
        assert "—" not in t, f
        assert not emoji.search(t), f


def test_every_page_has_viewport_and_sources_footer():
    for f in ["index.html", "agency.html", "evidence.html"]:
        t = (SITE / f).read_text(encoding="utf-8")
        assert 'name="viewport"' in t and 'id="sources"' in t
