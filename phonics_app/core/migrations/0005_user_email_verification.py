"""
Add email verification fields to User model
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_alter_user_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="user",
            name="email_verified_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
