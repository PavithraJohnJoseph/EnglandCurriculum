from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver


# ==========================
# PLAN MODEL
# ==========================
class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    access_years = models.JSONField()  # Example: [2012, 2013, 2014]
    audio_enabled = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    demo = models.BooleanField(default=False)

    stripe_price_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# ==========================
# CUSTOM USER
# ==========================
class User(AbstractUser):
    email = models.EmailField(unique=True)  # Ensure one email per user
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    last_page = models.IntegerField(default=0)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    def has_active_subscription(self) -> bool:
        return Subscription.objects.filter(
            user=self, active=True, end_date__gte=timezone.now().date()
        ).exists()

    def __str__(self) -> str:
        return self.username


# ==========================
# SUBSCRIPTION (YEARLY ONLY)
# ==========================
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    active = models.BooleanField(default=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = timezone.now().date() + timedelta(days=365)
        super().save(*args, **kwargs)

    def is_valid(self):
        return self.active and self.end_date >= timezone.now().date()

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"


# ==========================
# PAPER YEAR
# ==========================
class PaperYear(models.Model):
    year = models.IntegerField(unique=True)
    title_pdf = models.FileField(upload_to="papers/")

    def __str__(self):
        return str(self.year)


# ==========================
# PAPER PAGES (AUTO-SPLIT FROM PDF)
# ==========================
class PaperPage(models.Model):
    paper = models.ForeignKey(PaperYear, on_delete=models.CASCADE, related_name="pages")
    page_number = models.IntegerField()
    image = models.ImageField(upload_to="paper_images/")
    is_title = models.BooleanField(default=False)  # new field

    class Meta:
        ordering = ["page_number"]
        unique_together = ("paper", "page_number")

    def __str__(self):
        return f"{self.paper.year} - Page {self.page_number}"


# ==========================
# WORD MODEL (4 PER PAGE)
# ==========================
class Word(models.Model):
    page = models.ForeignKey(PaperPage, on_delete=models.CASCADE, related_name="words")
    text = models.CharField(max_length=50)
    type = models.CharField(
        max_length=10, choices=[("real", "Real"), ("pseudo", "Pseudo")]
    )
    audio_file = models.FileField(upload_to="word_audio/")
    hint1 = models.CharField(max_length=50, blank=True)
    hint2 = models.CharField(max_length=50, blank=True)
    hint3 = models.CharField(max_length=50, blank=True)
    highlight1 = models.CharField(max_length=10, blank=True)
    highlight2 = models.CharField(max_length=10, blank=True)
    highlight3 = models.CharField(max_length=10, blank=True)
    order = models.IntegerField(default=1)

    class Meta:
        ordering = ["order"]
        unique_together = ("page", "order")

    def __str__(self):
        return self.text


# ==========================
# USER PROGRESS TRACKING
# ==========================
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    paper_year = models.ForeignKey(PaperYear, on_delete=models.CASCADE)
    pages_completed = models.IntegerField(default=0)
    words_attempted = models.IntegerField(default=0)
    audio_used = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "paper_year")

    def __str__(self):
        return f"{self.user.username} - {self.paper_year.year}"


class AppSettings(models.Model):
    """Singleton-style app settings editable in Django admin."""

    paper_page_color_cycle = models.JSONField(
        default=list,
        help_text="List of hex colors used in page order for speech bubble themes.",
    )

    def __str__(self):
        return "Application Settings"


class Profile(models.Model):

    PLAN_CHOICES = [
        ("bronze", "Bronze"),
        ("silver", "Silver"),
        ("gold", "Gold"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default="bronze")

    def __str__(self):
        return f"{self.user.username} - {self.plan}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
