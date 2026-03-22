from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    AppSettings,
    Plan,
    User,
    Subscription,
    PaperYear,
    PaperPage,
    Word,
    UserProgress,
)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "audio_enabled", "is_free", "demo"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ("plan",)
    fieldsets = BaseUserAdmin.fieldsets + (
        (None, {"fields": ("plan", "last_page", "stripe_customer_id")}),
    )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "start_date", "end_date", "active"]


@admin.register(PaperYear)
class PaperYearAdmin(admin.ModelAdmin):
    list_display = ["year"]


@admin.register(PaperPage)
class PaperPageAdmin(admin.ModelAdmin):
    list_display = ["paper", "page_number"]


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ["text", "type", "page", "order"]


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "paper_year",
        "pages_completed",
        "words_attempted",
        "audio_used",
        "completed",
        "last_accessed",
    ]


@admin.register(AppSettings)
class AppSettingsAdmin(admin.ModelAdmin):
    list_display = ["id"]
    fields = ["paper_page_color_cycle"]

    def has_add_permission(self, request):
        # Keep a single settings row to avoid conflicting config.
        if AppSettings.objects.exists():
            return False
        return super().has_add_permission(request)
