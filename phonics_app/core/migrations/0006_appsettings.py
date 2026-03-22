from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_user_email_verification"),
    ]

    operations = [
        migrations.CreateModel(
            name="AppSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "paper_page_color_cycle",
                    models.JSONField(
                        default=list,
                        help_text="List of hex colors used in page order for speech bubble themes.",
                    ),
                ),
            ],
        ),
    ]
