import argparse
import os
import sys
from pathlib import Path
import re

import django
import pandas as pd

# Current file: core/scripts/setup_all_years.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # phonics_app/core
PROJECT_DIR = os.path.dirname(BASE_DIR)  # phonics_app

# Add project folder to Python path
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phonics_app.settings")
django.setup()

from core.models import PaperPage, PaperYear, Word  # noqa: E402
from core.utils import generate_audio_for_words, import_words_from_excel  # noqa: E402

EXCEL_FILE = Path(PROJECT_DIR) / "media" / "words.xlsx"
PAPER_IMAGES_ROOT = Path(PROJECT_DIR) / "media" / "paper_images"


def _find_page_image(year: int, page_number: int) -> Path | None:
    """Return an existing image path for a page (supports png/jpg/jpeg)."""
    year_dir = PAPER_IMAGES_ROOT / str(year)
    for ext in ("png", "jpg", "jpeg"):
        candidate = year_dir / f"page_{page_number}.{ext}"
        if candidate.exists():
            return candidate
    return None


def _list_available_image_page_numbers(year: int) -> list[int]:
    year_dir = PAPER_IMAGES_ROOT / str(year)
    if not year_dir.exists():
        return []

    page_numbers = []
    for child in year_dir.iterdir():
        match = re.match(r"page_(\d+)\.(png|jpg|jpeg)$", child.name, re.IGNORECASE)
        if match:
            page_numbers.append(int(match.group(1)))
    return sorted(set(page_numbers))


def normalize_title_pages(year: int) -> None:
    paper = PaperYear.objects.get(year=year)
    first_page = PaperPage.objects.filter(paper=paper, page_number=1).first()
    if not first_page:
        return

    needs_shift = (not first_page.is_title) or Word.objects.filter(page=first_page).exists()

    if needs_shift:
        max_word_page_number = (
            Word.objects.filter(page__paper=paper)
            .values_list("page__page_number", flat=True)
            .order_by("-page__page_number")
            .first()
        )
        if max_word_page_number:
            for page_number in range(int(max_word_page_number), 0, -1):
                source_page = PaperPage.objects.filter(paper=paper, page_number=page_number).first()
                target_page = PaperPage.objects.filter(paper=paper, page_number=page_number + 1).first()
                if source_page and target_page:
                    Word.objects.filter(page=source_page).update(page=target_page)

    PaperPage.objects.filter(paper=paper, page_number=1).update(is_title=True)
    PaperPage.objects.filter(paper=paper).exclude(page_number=1).update(is_title=False)


def setup_pages_from_excel(excel_path: Path) -> None:
    if not excel_path.exists():
        print(f"ERROR: Excel file not found: {excel_path}")
        return

    df = pd.read_excel(excel_path)
    df.columns = df.columns.str.strip()

    required = {"Year", "page_number"}
    missing = required - set(df.columns)
    if missing:
        print(f"ERROR: Missing required Excel columns: {sorted(missing)}")
        return

    # Keep only rows that can map to an actual year/page.
    scoped = df[["Year", "page_number"]].dropna()

    created_years = 0
    created_pages = 0

    for year in sorted(scoped["Year"].astype(int).unique().tolist()):
        paper, year_created = PaperYear.objects.get_or_create(year=year)
        if year_created:
            created_years += 1
            print(f"Created PaperYear {year}")
        else:
            print(f"PaperYear {year} already exists")

        year_pages = _list_available_image_page_numbers(year)

        for page_number in year_pages:
            image_path = _find_page_image(year, page_number)
            if image_path is None:
                print(
                    f"Page image missing for year {year}, page {page_number} "
                    f"(expected page_<n>.png/jpg/jpeg)"
                )
                continue

            relative_image = f"paper_images/{year}/{image_path.name}"
            page_obj, page_created = PaperPage.objects.get_or_create(
                paper=paper,
                page_number=page_number,
                defaults={"image": relative_image},
            )

            # If page exists without image, repair it.
            if not page_created and not page_obj.image:
                page_obj.image = relative_image
                page_obj.save(update_fields=["image"])

            if page_created:
                created_pages += 1
                print(f"Imported page {year}/{page_number}")
            else:
                print(f"Page {year}/{page_number} already exists, skipped")

        normalize_title_pages(year)

    print("\nPage setup summary:")
    print(f"  New years: {created_years}")
    print(f"  New pages: {created_pages}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Set up all years from words.xlsx and generate optional audio"
    )
    parser.add_argument(
        "--skip-audio",
        action="store_true",
        help="Skip audio generation step",
    )
    args = parser.parse_args()

    print(f"Using Excel: {EXCEL_FILE}")
    print(f"Using images root: {PAPER_IMAGES_ROOT}")

    # 1) Create PaperYear/PaperPage records for every year/page in Excel.
    setup_pages_from_excel(EXCEL_FILE)

    # 2) Import words for all available years from one Excel file.
    if EXCEL_FILE.exists():
        import_words_from_excel(str(EXCEL_FILE))
        print(f"Words imported from {EXCEL_FILE}")
    else:
        print(f"Excel file not found: {EXCEL_FILE}")
        return

    # 3) Generate audio files for all words (optional).
    if args.skip_audio:
        print("Skipped audio generation (--skip-audio)")
    else:
        generate_audio_for_words()
        print("Audio generation complete for all words")


if __name__ == "__main__":
    main()
