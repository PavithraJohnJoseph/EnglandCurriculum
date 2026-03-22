from django.shortcuts import redirect
from django.urls import resolve
from django.contrib import messages
from django.contrib.messages.api import MessageFailure


class EmailVerificationRequiredMiddleware:
    """Block authenticated but unverified users from protected routes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip checks for anonymous users.
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Superusers can always access.
        if request.user.is_superuser:
            return self.get_response(request)

        # If already verified, proceed.
        if getattr(request.user, "email_verified", False):
            request.session.pop("email_verify_warning_shown", None)
            return self.get_response(request)

        allowed_prefixes = [
            "/email-verification-pending/",
            "/verify-email/",
            "/resend-verification-email/",
            "/logout/",
            "/admin/",
            "/static/",
            "/media/",
            "/stripe-webhook/",
        ]

        if any(request.path.startswith(prefix) for prefix in allowed_prefixes):
            return self.get_response(request)


        if not request.session.get("email_verify_warning_shown", False):
            # Prevent duplicate warning messages
            existing_warnings = [str(m) for m in messages.get_messages(request)]
            warning_text = "Please verify your email to continue to Dashboard."
            if warning_text not in existing_warnings:
                try:
                    messages.warning(
                        request,
                        warning_text,
                    )
                except MessageFailure:
                    # If messages middleware is unavailable in a given environment,
                    # continue redirect flow without failing the request.
                    pass
            request.session["email_verify_warning_shown"] = True

        return redirect("core:email_verification_pending")


class AccessControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed_paths = [
            "/admin/",
            "/login/",
            "/signup/",
            "/logout/",
            "/stripe-webhook/",
            "/upgrade/",
        ]

        if any(request.path.startswith(path) for path in allowed_paths):
            return self.get_response(request)

        if not request.user.is_authenticated:
            return redirect("login")

        user = request.user
        # Do not auto-downgrade immediately; paid plan activation can arrive via
        # Stripe webhook shortly after checkout redirect.

        # Year access protection
        if "paper" in request.path:
            try:
                resolver = resolve(request.path)
                year = resolver.kwargs.get("year")
                if year and user.plan and int(year) not in user.plan.access_years:
                    return redirect("upgrade")
            except (ValueError, TypeError, AttributeError):
                pass

        # Audio access
        if request.GET.get("audio") == "1":
            if not user.plan or not user.plan.audio_enabled:
                return redirect("upgrade")

        return self.get_response(request)
