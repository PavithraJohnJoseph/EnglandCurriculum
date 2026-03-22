import os
import pandas as pd
from django.conf import settings
from django.core.files import File
from gtts import gTTS

from .models import PaperYear, PaperPage, Word


def _clean_excel_value(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


# =========================
# IMPORT WORDS FROM EXCEL
# =========================
def import_words_from_excel(excel_file):

    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return

    df = pd.read_excel(excel_file)
    df.columns = df.columns.str.strip()

    total_imported = 0
    total_skipped = 0

    model_fields = [field.name for field in Word._meta.fields]

    for _, row in df.iterrows():

        try:
            year = int(row["Year"])
            page_number = int(row["page_number"])
            text = _clean_excel_value(row.get("text", ""))
            word_type = _clean_excel_value(row.get("type", "")).lower()
            order = int(row.get("order", 1))
        except Exception as e:
            print(f"⚠ Skipping row → {e}")
            total_skipped += 1
            continue

        if not text:
            total_skipped += 1
            continue

        try:
            paper = PaperYear.objects.get(year=year)
            has_title_page = PaperPage.objects.filter(paper=paper, is_title=True).exists()
            display_page_number = page_number + 1 if has_title_page else page_number
            page = PaperPage.objects.get(paper=paper, page_number=display_page_number)
        except Exception as e:
            print(f"⚠ Page not found for '{text}' → {e}")
            total_skipped += 1
            continue

        defaults = {"text": text, "type": word_type, "order": order}

        optional_fields = [
            "hint1",
            "hint2",
            "hint3",
            "highlight1",
            "highlight2",
            "highlight3",
        ]

        for field in optional_fields:
            if field in model_fields and field in row:
                value = _clean_excel_value(row.get(field, ""))
                defaults[field] = value

        word, created = Word.objects.get_or_create(
            page=page, order=order, defaults=defaults
        )

        if created:
            total_imported += 1
        else:
            changed = False
            for key, value in defaults.items():
                if getattr(word, key) != value:
                    setattr(word, key, value)
                    changed = True

            if changed:
                word.save()
                total_imported += 1
            else:
                total_skipped += 1

    print(f"\n✅ Imported: {total_imported}")
    print(f"⚠ Skipped: {total_skipped}")


# =========================
# IMPORT PAGE IMAGES
# =========================
def import_year_pages(year):
    try:
        paper = PaperYear.objects.get(year=year)
    except PaperYear.DoesNotExist:
        print(f"❌ PaperYear {year} not found.")
        return

    folder_path = os.path.join(settings.MEDIA_ROOT, f"paper_images/{year}")

    if not os.path.exists(folder_path):
        print(f"❌ Folder not found: {folder_path}")
        return

    for i in range(1, 12):
        file_name = f"page_{i}.png"
        file_path = os.path.join(folder_path, file_name)

        if not os.path.exists(file_path):
            print(f"⚠ Missing file: {file_name}")
            continue

        page, created = PaperPage.objects.get_or_create(
            paper=paper,
            page_number=i,
        )

        if created:
            with open(file_path, "rb") as f:
                page.image.save(f"paper_images/{year}/{file_name}", File(f), save=True)
            print(f"✅ Imported page {i} for year {year}")
        else:
            print(f"⚠ Page {i} already exists, skipped.")


# =========================
# GENERATE AUDIO
# =========================
def generate_audio_for_words():

    audio_dir = os.path.join(settings.MEDIA_ROOT, "word_audio")
    os.makedirs(audio_dir, exist_ok=True)

    words = Word.objects.all()
    total = words.count()

    print(f"\n🎵 Generating audio for {total} words...")

    for idx, word in enumerate(words, 1):

        safe_text = "".join(
            c for c in word.text if c.isalnum() or c in (" ", "_")
        ).replace(" ", "_")

        filename = f"{safe_text}.mp3"
        filepath = os.path.join(audio_dir, filename)

        if not os.path.exists(filepath):
            try:
                tts = gTTS(text=word.text, lang="en")
                tts.save(filepath)
                print(f"[{idx}/{total}] ✅ Generated: {filename}")
            except Exception as e:
                print(f"[{idx}/{total}] ❌ Failed: {word.text} → {e}")
                continue
        else:
            print(f"[{idx}/{total}] ⚠ Already exists: {filename}")

        relative_path = f"word_audio/{filename}"

        if not word.audio_file or word.audio_file.name != relative_path:
            word.audio_file.name = relative_path
            word.save()

    print("\n✅ Audio generation complete!")
