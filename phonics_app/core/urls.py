from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("health/", views.health_check, name="health_check"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Plan and payment flow
    path("plans/", views.plan_selection, name="plan_selection"),
    path("years/", views.year_selection, name="year_selection"),
    path(
        "year-selection/",
        RedirectView.as_view(pattern_name="core:year_selection", permanent=False),
        name="year_selection_legacy",
    ),
    path("payment/<int:plan_id>/", views.payment, name="payment"),
    # password reset flow
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="core/password_reset_form.html",
            email_template_name="core/password_reset_email.html",
            success_url=reverse_lazy("core:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="core/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="core/password_reset_confirm.html",
            success_url=reverse_lazy("core:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="core/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "paper/<int:paper_id>/page/<int:page_number>/",
        views.paper_page,
        name="paper_page",
    ),
    # Email verification
    path(
        "email-verification-pending/",
        views.email_verification_pending,
        name="email_verification_pending",
    ),
    path("verify-email/<uidb64>/<token>/", views.verify_email, name="verify_email"),
    path(
        "resend-verification-email/",
        views.resend_verification_email,
        name="resend_verification_email",
    ),
    # Stripe webhook
    path("stripe-webhook/", views.stripe_webhook, name="stripe_webhook"),
    # Test email (debug only)
    path("test-email/", views.test_email, name="test_email"),
    # Auth routes
    path("signup/", views.signup_view, name="signup"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="core:dashboard"),
        name="logout",
    ),
]
