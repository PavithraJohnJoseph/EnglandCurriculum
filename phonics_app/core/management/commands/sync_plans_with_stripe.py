"""
Management command to sync plans with Stripe
Creates Stripe products and prices for each plan in the database
"""

from django.core.management.base import BaseCommand
from core.models import Plan
from core.stripe_utils import sync_plan_with_stripe


class Command(BaseCommand):
    help = "Sync all plans with Stripe. Creates products and prices for each plan."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force re-sync of all plans even if they already have stripe_price_id",
        )

    def handle(self, *args, **options):
        plans = Plan.objects.all()
        force = options.get("force", False)

        if not plans.exists():
            self.stdout.write(self.style.ERROR("No plans found in database"))
            return

        synced = 0
        skipped = 0
        errors = 0

        for plan in plans:
            if plan.stripe_price_id and not force:
                self.stdout.write(
                    self.style.WARNING(
                        f"⊘ {plan.name}: Already synced "
                        f"(stripe_price_id={plan.stripe_price_id})"
                    )
                )
                skipped += 1
                continue

            try:
                price_id = sync_plan_with_stripe(plan)
                self.stdout.write(
                    self.style.SUCCESS(f"✓ {plan.name}: Synced (price_id={price_id})")
                )
                synced += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ {plan.name}: {str(e)}"))
                errors += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"✓ Synced: {synced}"))
        self.stdout.write(self.style.WARNING(f"⊘ Skipped: {skipped}"))
        self.stdout.write(self.style.ERROR(f"✗ Errors: {errors}"))
