import os
import django
import sys

# Current file: core/scripts/setup_2012.py
BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)  # phonics_app/core
PROJECT_DIR = os.path.dirname(BASE_DIR)  # phonics_app

# Add project folder to Python path
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phonics_app.settings")
django.setup()

from core.models import PaperYear, PaperPage  # noqa: E402
from core.utils import import_words_from_excel, generate_audio_for_words  # noqa: E402

YEAR = 2012
MEDIA_ROOT = "media/paper_images/2012"
EXCEL_FILE = "media/words.xlsx"  # Update path if different

# -----------------------------
# 1️⃣ Create PaperYear
# -----------------------------
paper, created = PaperYear.objects.get_or_create(year=YEAR)
if created:
    print(f"Created PaperYear {YEAR}")
else:
    print(f"PaperYear {YEAR} already exists")

# -----------------------------
# 2️⃣ Import Pages (skip existing)
# -----------------------------
for i in range(1, 12):  # pages 1 to 11
    page_path = os.path.join(MEDIA_ROOT, f"page_{i}.png")
    if not os.path.exists(page_path):
        print(f"Page image missing: {page_path}")
        continue

    page_obj, created = PaperPage.objects.get_or_create(
        paper=paper,
        page_number=i,
        defaults={"image": f"paper_images/2012/page_{i}.png"},
    )
    if created:
        print(f"Imported page {i}")
    else:
        print(f"Page {i} already exists, skipped")

# -----------------------------
# 3️⃣ Import Words from Excel
# -----------------------------
if os.path.exists(EXCEL_FILE):
    import_words_from_excel(EXCEL_FILE)
    print(f"Words imported from {EXCEL_FILE}")
else:
    print(f"Excel file not found: {EXCEL_FILE}")

# -----------------------------
# 4️⃣ Generate Audio for Words
# -----------------------------
generate_audio_for_words()
print("✅ Audio generation complete for all words!")
