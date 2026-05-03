"""
assign_photos.py  —  replaces placeholder divs with real <img> tags
Usage:
    python assign_photos.py            # dry run
    python assign_photos.py --write    # apply changes (saves .bak first)
"""
import argparse, shutil
from pathlib import Path
from bs4 import BeautifulSoup

HTML_FILE = Path(__file__).parent / "Grand Terraza Landing.html"

SLOT_MAP = [
    {"identify_by": "gt-hero__img",    "src": "images/hero/hero.jpg",                      "alt": "Grand Terraza Event Center"},
    {"identify_by": "gt-about__img-1", "src": "images/about/about-portrait.jpg",            "alt": "Grand Terraza exterior at twilight"},
    {"identify_by": "gt-about__img-2", "src": "images/about/about-detail.jpg",              "alt": "Table setting detail"},
    {"identify_by_text": "THE GRAND HALL",         "src": "images/spaces/space-grand-hall.jpg",        "alt": "The Grand Hall interior"},
    {"identify_by_text": "THE GARDEN TERRAZA",     "src": "images/spaces/space-garden-terraza.jpg",    "alt": "The Garden Terraza"},
    {"identify_by_text": "THE BRIDAL QUARTERS",    "src": "images/spaces/space-bridal-quarters.jpg",   "alt": "The Bridal Quarters"},
    {"identify_by_text": "THE OAK PAVILION",       "src": "images/spaces/space-oak-pavilion.jpg",      "alt": "The Oak Pavilion"},
    {"identify_by_text": "CEREMONY ARCH",          "src": "images/gallery/gallery-01-ceremony.jpg",    "alt": "Ceremony arch"},
    {"identify_by_text": "RECEPTION",              "src": "images/gallery/gallery-02-reception.jpg",   "alt": "Long-table reception"},
    {"identify_by_text": "BRIDE",                  "src": "images/gallery/gallery-03-bride.jpg",       "alt": "Bride at golden hour"},
    {"identify_by_text": "STRING LIGHTS",          "src": "images/gallery/gallery-04-lights.jpg",      "alt": "String lights in the Oak Pavilion"},
    {"identify_by_text": "FLORALS",                "src": "images/gallery/gallery-05-florals.jpg",     "alt": "Floral arrangement"},
    {"identify_by_text": "FIRST DANCE",            "src": "images/gallery/gallery-06-dance.jpg",       "alt": "First dance"},
    {"identify_by_text": "TABLESCAPE",             "src": "images/gallery/gallery-07-tablescape.jpg",  "alt": "Tablescape in gold and plum"},
]


def replace_placeholder(soup, slot):
    ph = None
    if "identify_by" in slot:
        ph = soup.find("div", class_=lambda c: c and slot["identify_by"] in c.split())
    else:
        for div in soup.find_all("div", class_="placeholder"):
            span = div.find("span")
            if span and slot["identify_by_text"].lower() in span.get_text().lower():
                ph = div
                break

    if ph is None:
        key = slot.get("identify_by") or slot.get("identify_by_text")
        print(f"  [SKIP] could not find: {key}")
        return False

    keep = [c for c in ph.get("class", [])
            if c != "placeholder" and not c.startswith("tone-")]

    orig_style = ph.get("style", "").replace("min-height:100vh", "").strip().strip(";")
    style_parts = ["width:100%", "height:100%", "object-fit:cover", "display:block"]
    if orig_style:
        style_parts.insert(0, orig_style)

    img = soup.new_tag("img", src=slot["src"], alt=slot["alt"])
    img["class"] = keep
    img["style"] = ";".join(style_parts)
    ph.replace_with(img)
    print(f"  [OK]   {slot['src']}")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write changes to file")
    args = parser.parse_args()

    html = HTML_FILE.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "html.parser")

    print(f"\nProcessing: {HTML_FILE}\n")
    ok = sum(replace_placeholder(soup, s) for s in SLOT_MAP)
    print(f"\n{ok}/{len(SLOT_MAP)} placeholders replaced.")

    if not args.write:
        print("Dry run — add --write to apply changes.")
        return

    bak = HTML_FILE.with_suffix(".html.bak")
    shutil.copy(HTML_FILE, bak)
    HTML_FILE.write_text(str(soup), encoding="utf-8")
    print(f"Saved. Backup at: {bak}")


if __name__ == "__main__":
    main()
