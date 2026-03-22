from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_appsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="hint3",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="word",
            name="highlight3",
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
