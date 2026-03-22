from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .forms import SignUpForm, LoginForm
from .models import AppSettings, PaperYear, PaperPage, Word, UserProgress, Plan, User
from .stripe_utils import (
    create_checkout_session,
    finalize_checkout_from_session_id,
    handle_checkout_session_completed,
    verify_webhook_signature,
)
from .email_utils import (
    send_welcome_email,
    send_email_verification,
    send_subscription_confirmation_email,
)
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from typing import Optional
from django.http import HttpRequest, HttpResponse
import logging
from .tokens import email_verification_token


logger = logging.getLogger(__name__)


# ==========================
# HEALTH CHECK
# ==========================
def health_check(request: HttpRequest) -> JsonResponse:
    """Health check endpoint for monitoring and load balancers"""
    try:
        # Check database connection
        Plan.objects.exists()
        return JsonResponse(
            {"status": "healthy", "message": "Service is healthy"}, status=200
        )
    except Exception as e:
        return JsonResponse({"status": "unhealthy", "error": str(e)}, status=503)


# ==========================
# HOME PAGE
# ==========================
def home(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect("core:dashboard")
    return render(request, "core/home.html")


# ==========================
# PLAN SELECTION
# ==========================
def plan_selection(request: HttpRequest) -> HttpResponse:
    plans = Plan.objects.all().order_by("price")
    current_plan = request.user.plan if request.user.is_authenticated else None
    next_upgrade_plan = None

    if current_plan:
        next_upgrade_plan = (
            Plan.objects.filter(price__gt=current_plan.price)
            .order_by("price")
            .first()
        )

    return render(
        request,
        "core/plan_selection.html",
        {
            "plans": plans,
            "current_plan": current_plan,
            "next_upgrade_plan": next_upgrade_plan,
        },
    )


# ==========================
# YEAR SELECTION
# ==========================
@login_required
def year_selection(request):
    def _requeue_non_payment_messages(req):
        buffered = []
        for msg in get_messages(req):
                # ...existing code...
                # Placeholder for filtering logic, since variables are not defined here
                buffered.append((msg.level, str(msg), msg.extra_tags))

        for level, text, extra_tags in buffered:
            messages.add_message(req, level, text, extra_tags=extra_tags)

    user = request.user
    if not user.plan:
        return redirect("core:plan_selection")

    # Fallback finalization when user returns from Stripe success URL.
    session_id = request.GET.get("session_id")
    if session_id:
        processed_session_ids = set(request.session.get("processed_checkout_sessions", []))
        if session_id in processed_session_ids:
            return redirect("core:year_selection")

        try:
            finalize_checkout_from_session_id(user, session_id)
            user.refresh_from_db()
            _requeue_non_payment_messages(request)
            messages.success(
                request,
                f"Payment confirmed. {user.plan.name} is now active.",
            )
            processed_session_ids.add(session_id)
            request.session["processed_checkout_sessions"] = list(processed_session_ids)
        except Exception as e:
            logger.error(f"Failed to finalize checkout from session_id: {str(e)}")
            _requeue_non_payment_messages(request)
            messages.warning(
                request,
                "Payment is processing. Please refresh in a few moments.",
            )

    # Get all available years from plans
    all_years = set()
    for plan in Plan.objects.all():
        all_years.update(plan.access_years)
    all_years = sorted(all_years)

    # Determine which years are accessible for this user
    accessible_years = set(user.plan.access_years) if user.plan else set()

    years_data = []
    for year in all_years:
        paper = PaperYear.objects.filter(year=year).first()
        years_data.append(
            {
                "year": year,
                "accessible": year in accessible_years,
                "paper_exists": paper is not None,
                "paper_id": paper.id if paper else None,
            }
        )

    next_upgrade_plan = None
    if user.plan:
        next_upgrade_plan = (
            Plan.objects.filter(price__gt=user.plan.price)
            .order_by("price")
            .first()
        )

    return render(
        request,
        "core/year_selection.html",
        {
            "years_data": years_data,
            "user_plan": user.plan,
            "next_upgrade_plan": next_upgrade_plan,
        },
    )


# ==========================
# PAYMENT PROCESSING
# ==========================
@login_required
def payment(request, plan_id):
    plan = get_object_or_404(Plan, id=plan_id)
    current_plan = request.user.plan
    next_upgrade_plan = None

    if current_plan:
        next_upgrade_plan = (
            Plan.objects.filter(price__gt=current_plan.price)
            .order_by("price")
            .first()
        )

    # Bronze is free, redirect to year selection
    if plan.is_free:
        request.user.plan = plan
        request.user.save()
        return redirect("core:year_selection")

    # For paid plans, create Stripe checkout session
    if request.method == "POST":
        try:
            session = create_checkout_session(request.user, plan)
            return redirect(session.url)
        except Exception as e:
            # On error, render payment page with error message
            context = {
                "plan": plan,
                "current_plan": current_plan,
                "next_upgrade_plan": next_upgrade_plan,
                "error": f"Failed to initiate payment: {str(e)}",
            }
            return render(request, "core/payment.html", context)

    # GET: Show payment form with Stripe integration
    context = {
        "plan": plan,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
        "current_plan": current_plan,
        "next_upgrade_plan": next_upgrade_plan,
    }
    return render(request, "core/payment.html", context)


# ==========================
# DASHBOARD
# ==========================
@login_required
def dashboard(request):
    user = request.user

    # If user has no plan, redirect to plan selection
    if not user.plan:
        return redirect("core:plan_selection")

    if user.plan:
        years = user.plan.access_years
        papers = PaperYear.objects.filter(year__in=years)
    else:
        papers = PaperYear.objects.none()
    return render(request, "core/dashboard.html", {"papers": papers})


# ==========================
# LOGIN
# ==========================
def login_view(request):
    # Always start with empty form data for GET requests to ensure blank fields
    if request.method == "GET":
        form = LoginForm()
    else:
        form = LoginForm(request, data=request.POST)

    if form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect("core:dashboard")
    return render(request, "core/login.html", {"form": form})


# ==========================
# SIGNUP
# ==========================
def signup_view(request):
    form = SignUpForm(request.POST or None)
    if form.is_valid():
        user = form.save()

        # Defensive fallback: ensure signup users start on a free/default plan.
        if not user.plan:
            default_plan = Plan.objects.filter(is_free=True).order_by("price", "id").first()
            if default_plan:
                user.plan = default_plan
                user.save(update_fields=["plan"])

        # Auto-login first. Django's default token generator includes last_login,
        # so verification email must be generated after login updates that field.
        login(request, user)

        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception as e:
            # Log error but don't block signup
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")

        # Send email verification (after login to avoid immediate token invalidation)
        try:
            send_email_verification(user)
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to send verification email to {user.email}: {str(e)}")

        return redirect("core:email_verification_pending")
    return render(request, "core/signup.html", {"form": form})


# ==========================
# LOGOUT
# ==========================
def logout_view(request):
    logout(request)
    return redirect("core:login")


# ==========================
# EMAIL VERIFICATION
# ==========================
@login_required
def email_verification_pending(request):
    """Show pending email verification page"""
    user = request.user

    # Remove stale Stripe flash messages here to avoid confusing new users.
    # This page should focus on email verification status only.
    buffered_messages = []
    seen_texts = set()
    verify_warning_seen = False
    for msg in get_messages(request):
        msg_text = str(msg)
        if msg_text.startswith("Payment confirmed.") or msg_text.startswith("Payment is processing."):
            continue
        normalized_text = msg_text.strip().lower()
        # Only allow one verify warning message
        if normalized_text == "please verify your email to continue to dashboard.":
            if verify_warning_seen:
                continue
            verify_warning_seen = True
        if normalized_text in seen_texts:
            continue
        seen_texts.add(normalized_text)
        buffered_messages.append((msg.level, msg_text, msg.extra_tags))

    for level, text, extra_tags in buffered_messages:
        messages.add_message(request, level, text, extra_tags=extra_tags)

    # Clear the session flag so the warning is not shown again until next redirect
    request.session.pop("email_verify_warning_shown", None)
    context = {"email": user.email, "email_verified": user.email_verified}
    return render(request, "core/email_verification_pending.html", context)


def verify_email(request, uidb64, token):
    """Verify email via link"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and email_verification_token.check_token(user, token):
        # Email verification successful
        user.email_verified = True
        user.email_verified_at = timezone.now()
        user.save()

        # Log user in if not already logged in
        if not request.user.is_authenticated:
            login(request, user)

        return render(request, "core/email_verification_success.html", {"user": user})
    else:
        # Invalid token or user
        return render(
            request,
            "core/email_verification_failure.html",
            {"token_invalid": True},
            status=400,
        )


@login_required
@require_http_methods(["POST"])
def resend_verification_email(request):
    """Resend email verification link for the current logged-in user."""
    user = request.user

    if user.email_verified:
        messages.info(request, "Your email is already verified.")
        return redirect("core:email_verification_pending")

    try:
        result = send_email_verification(user)
        if result:
            messages.success(
                request,
                f"A new verification email has been sent to {user.email}.",
            )
        else:
            messages.error(
                request,
                "Could not send verification email right now. Please try again.",
            )
    except Exception as e:
        logger.error(f"Failed to resend verification email to {user.email}: {str(e)}")
        messages.error(
            request,
            "Could not send verification email right now. Please try again.",
        )

    return redirect("core:email_verification_pending")


# ==========================
# PAPER PAGE VIEW
# Handles page navigation, words, audio mode, and celebration
# ==========================
# ==========================
# PAPER PAGE VIEW
# Handles page navigation, words, audio mode, and celebration
# ==========================
@login_required
def paper_page(request, paper_id, page_number):
    user = request.user

    # Check if user has a plan
    if not user.plan:
        return redirect("core:plan_selection")

    paper = get_object_or_404(PaperYear, id=paper_id)

    # Check if user has access to this year
    if paper.year not in user.plan.access_years:
        return redirect("core:year_selection")

    page = get_object_or_404(PaperPage, paper=paper, page_number=page_number)

    # ==========================
    # Determine words for current page
    # ==========================
    if page.is_title:
        words = []  # no words on title page
        is_title = True
    else:
        # Each practice page should present 4 words. Limit to the first four
        # to guard against legacy stale rows from older imports.
        words = Word.objects.filter(page=page).order_by("order")[:4]
        is_title = False

    # ==========================
    # Get or create progress record
    # ==========================
    progress, _ = UserProgress.objects.get_or_create(user=user, paper_year=paper)

    # Auto-audio is enabled by plan. Query param still supported for backward compatibility.
    audio_mode = bool(user.plan and user.plan.audio_enabled) or request.GET.get("audio") == "1"
    auto_sequence = request.GET.get("autoplay") == "1"
    if audio_mode:
        progress.audio_used = True

    # Track words attempted
    if request.method == "POST":
        progress.words_attempted += len(words)
        progress.pages_completed = page_number
        progress.save()

    # Check for celebration: last page of paper
    last_page_number = PaperPage.objects.filter(paper=paper).count()
    celebrate = False
    if page_number == last_page_number:
        celebrate = True
        progress.completed = True
        progress.save()

    # Determine previous / next page numbers
    prev_page = page_number - 1 if page_number > 1 else None
    next_page = page_number + 1 if page_number < last_page_number else None
    next_page_url = None
    if next_page:
        next_page_url = f"/paper/{paper.id}/page/{next_page}/"
        if auto_sequence:
            next_page_url += "?autoplay=1"

    admin_settings = AppSettings.objects.first()
    color_cycle = (
        admin_settings.paper_page_color_cycle
        if admin_settings and admin_settings.paper_page_color_cycle
        else getattr(settings, "PAPER_PAGE_COLOR_CYCLE", None)
    ) or [
        "#8A2BE2",
        "#4B0082",
        "#1E90FF",
        "#2E8B57",
        "#FF8C00",
    ]
    speech_color = color_cycle[(page_number - 1) % len(color_cycle)]
    highlight_color = color_cycle[page_number % len(color_cycle)]

    context = {
        "paper": paper,
        "page": page,
        "words": words,
        "celebrate": celebrate,
        "audio_mode": audio_mode,
        "auto_sequence": auto_sequence,
        "prev_page": prev_page,
        "next_page": next_page,
        "next_page_url": next_page_url,
        "last_page_number": last_page_number,
        "is_title": is_title,  # pass to template
        "speech_color": speech_color,
        "highlight_color": highlight_color,
        # 'plans': plans,  # not currently used but left for future
    }
    return render(request, "core/paper_page.html", context)


# ==========================
# USER PROGRESS
# ==========================
@login_required
def progress_view(request):
    user = request.user
    progress_list = UserProgress.objects.filter(user=user)
    return render(request, "core/progress.html", {"progress_list": progress_list})


# ==========================
# TEST EMAIL (Development only)
# ==========================
@login_required
def test_email(request):
    """Test email view - for development/debugging only"""
    if not settings.DEBUG:
        return redirect("core:dashboard")

    user = request.user
    subject = "Test Email from Year 1 Phonics"
    message = f"""\
Hi {user.username},

This is a test email to verify password reset email configuration is working.

If you're seeing this, emails are being sent correctly!

Thanks,
The Year 1 Phonics team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        context = {"success": True, "message": f"Test email sent to {user.email}"}
    except Exception as e:
        context = {"success": False, "message": f"Error sending email: {str(e)}"}

    return render(request, "core/test_email.html", context)


# ==========================
# STRIPE WEBHOOK
# ==========================
@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Handle Stripe webhook events
    Processes payment confirmations, subscription updates, cancellations
    """
    try:
        body = request.body.decode("utf-8")
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

        event = verify_webhook_signature(body, sig_header)

        # Handle different event types
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            subscription = handle_checkout_session_completed(session)

            # Send subscription confirmation email
            try:
                user = subscription.user
                plan = subscription.plan
                send_subscription_confirmation_email(user, plan)
            except Exception as e:
                import logging

                logger = logging.getLogger(__name__)
                logger.error(
                    f"Failed to send subscription confirmation email: {str(e)}"
                )

        elif event["type"] == "customer.subscription.deleted":
            from .stripe_utils import handle_customer_subscription_deleted

            subscription = event["data"]["object"]
            handle_customer_subscription_deleted(subscription)

        elif event["type"] == "invoice.payment_failed":
            from .stripe_utils import handle_invoice_payment_failed

            invoice = event["data"]["object"]
            handle_invoice_payment_failed(invoice)

        return JsonResponse({"status": "success"}, status=200)

    except ValueError as e:
        # Invalid signature
        return JsonResponse({"error": str(e)}, status=403)
    except Exception as e:
        # Log webhook errors
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Stripe webhook error: {str(e)}")
        return JsonResponse({"error": str(e)}, status=400)
