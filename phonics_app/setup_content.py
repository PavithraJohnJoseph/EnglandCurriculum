#!/usr/bin/env python
"""
Content Setup Script for Year 1 Phonics App
Creates sample phonics papers, pages, and words for testing and demo purposes
"""

import os
import django
import sys

# Setup Django
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, PROJECT_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "phonics_app.settings")
django.setup()

from core.models import PaperYear, PaperPage, Word, Plan

def create_sample_content():
    """Create sample phonics content for demonstration"""

    print("🎯 Creating Sample Phonics Content")
    print("=" * 40)

        # Sample phonics data for Year 1 (simplified)
    phonics_data = {
        2012: {
            "pages": [
                {
                    "page_number": 1,
                    "is_title": True,
                    "words": [
                        ("sat", "s", "a", "t"),
                        ("pat", "p", "a", "t"),
                        ("mat", "m", "a", "t"),
                        ("tap", "t", "a", "p"),
                    ]
                },
                {
                    "page_number": 2,
                    "is_title": False,
                    "words": [
                        ("dog", "d", "o", "g"),
                        ("god", "g", "o", "d"),
                        ("cod", "c", "o", "d"),
                        ("cog", "c", "o", "g"),
                    ]
                }
            ]
        },
        2013: {
            "pages": [
                {
                    "page_number": 1,
                    "is_title": True,
                    "words": [
                        ("hat", "h", "a", "t"),
                        ("ham", "h", "a", "m"),
                        ("had", "h", "a", "d"),
                        ("bag", "b", "a", "g"),
                    ]
                }
            ]
        }
    }

    total_papers = 0
    total_pages = 0
    total_words = 0

    for year, data in phonics_data.items():
        # Create PaperYear
        paper_year, created = PaperYear.objects.get_or_create(year=year)
        if created:
            print(f"✓ Created PaperYear {year}")
            total_papers += 1
        else:
            print(f"✓ PaperYear {year} already exists")

        # Create pages and words
        for page_data in data["pages"]:
            page, page_created = PaperPage.objects.get_or_create(
                paper=paper_year,
                page_number=page_data["page_number"],
                defaults={"is_title": page_data["is_title"]}
            )

            if page_created:
                print(f"  ✓ Created Page {page.page_number}")
                total_pages += 1

            # Create words for this page
            for i, (word_text, *hints) in enumerate(page_data["words"], 1):
                word_type = "real" if len([h for h in hints if h]) == len(word_text.replace(" ", "")) else "pseudo"

                word, word_created = Word.objects.get_or_create(
                    page=page,
                    order=i,
                    defaults={
                        "text": word_text,
                        "type": word_type,
                        "hint1": hints[0] if len(hints) > 0 else "",
                        "hint2": hints[1] if len(hints) > 1 else "",
                        "highlight1": hints[0] if len(hints) > 0 else "",
                        "highlight2": hints[1] if len(hints) > 1 else "",
                    }
                )
                if word_created:
                    total_words += 1

    print("\n📊 Content Creation Summary:")
    print(f"  Papers: {total_papers}")
    print(f"  Pages: {total_pages}")
    print(f"  Words: {total_words}")

    # Create sample plans if they don't exist
    plans_data = [
        {"name": "Bronze Plan", "price": 0.00, "is_free": True, "access_years": [2012]},
        {"name": "Silver Plan", "price": 4.99, "is_free": False, "access_years": [2012, 2013, 2014, 2015]},
        {"name": "Gold Plan", "price": 9.99, "is_free": False, "access_years": [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2022, 2023, 2024, 2025]},
    ]

    print("\n💰 Setting up Subscription Plans:")
    for plan_data in plans_data:
        plan, created = Plan.objects.get_or_create(
            name=plan_data["name"],
            defaults={
                "price": plan_data["price"],
                "is_free": plan_data["is_free"],
                "access_years": plan_data["access_years"],
                "audio_enabled": True,
            }
        )
        if created:
            print(f"✓ Created {plan.name} (${plan.price})")
        else:
            print(f"✓ {plan.name} already exists")

    print("\n🎉 Sample content setup complete!")
    print("\nNext steps:")
    print("1. Upload paper images to media/paper_images/")
    print("2. Upload audio files to media/audio/ and media/word_audio/")
    print("3. Run: python manage.py setup_initial_data")

if __name__ == "__main__":
    create_sample_content()