"""
Management command to setup initial data (plans, etc.)
Usage: python manage.py setup_initial_data
"""

from django.core.management.base import BaseCommand
from core.models import Plan


class Command(BaseCommand):
    help = "Setup initial plans and data"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("🚀 Setting up initial data..."))

        # Create default plans
        plans = [
            {
                "name": "Bronze Plan",
                "price": 0.00,
                "access_years": [2012],
                "audio_enabled": True,
                "is_free": True,
                "demo": True,
            },
            {
                "name": "Silver Plan",
                "price": 4.99,
                "access_years": [2012, 2013, 2014, 2015],
                "audio_enabled": True,
                "is_free": False,
                "demo": False,
            },
            {
                "name": "Gold Plan",
                "price": 9.99,
                "access_years": [
                    2012,
                    2013,
                    2014,
                    2015,
                    2016,
                    2017,
                    2018,
                    2019,
                    2022,
                    2023,
                    2024,
                    2025,
                ],
                "audio_enabled": True,
                "is_free": False,
                "demo": False,
            },
        ]

        for plan_data in plans:
            plan, created = Plan.objects.update_or_create(
                name=plan_data["name"], defaults=plan_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Created plan: {plan.name}"))
            else:
                self.stdout.write(
                    self.style.WARNING(f"♻️  Updated plan: {plan.name}")
                )

        self.stdout.write(self.style.SUCCESS("✨ Initial data setup complete!"))
