"""
Email utility functions for sending transactional emails
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .tokens import email_verification_token
import logging

logger = logging.getLogger(__name__)


def _get_site_url() -> str:
    """Return a normalized absolute site URL with a safe fallback."""
    site_url = (getattr(settings, "SITE_URL", "") or "").strip()
    if not site_url:
        return "http://localhost:8000"

    # If someone sets SITE_URL without scheme, normalize it to http.
    if not site_url.startswith(("http://", "https://")):
        site_url = f"http://{site_url}"

    return site_url.rstrip("/")


def send_email(subject, template_name, context, recipient_list, html_template=None):
    """
    Generic email sending function with template support

    Args:
        subject: Email subject
        template_name: Path to text template
        context: Template context dict
        recipient_list: List of email addresses
        html_template: Path to HTML template (optional)

    Returns:
        Number of messages sent (0 or 1)
    """
    try:
        text_content = render_to_string(template_name, context)

        # If HTML template provided, create alternative
        if html_template:
            html_content = render_to_string(html_template, context)
            msg = EmailMultiAlternatives(
                subject, text_content, settings.DEFAULT_FROM_EMAIL, recipient_list
            )
            msg.attach_alternative(html_content, "text/html")
            result = msg.send()
        else:
            result = send_mail(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                recipient_list,
                fail_silently=False,
            )

        logger.info(f"Email sent: {subject} to {recipient_list}")
        return result
    except Exception as e:
        logger.error(f"Failed to send email '{subject}': {str(e)}")
        if settings.DEBUG:
            raise
        return 0


def send_welcome_email(user):
    """
    Send welcome email to new user after signup
    """
    site_url = _get_site_url()
    context = {
        "username": user.username,
        "email": user.email,
        "site_name": "Year 1 Phonics",
        "site_url": site_url,
    }

    return send_email(
        subject=f"Welcome to Year 1 Phonics, {user.username}!",
        template_name="emails/welcome.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/welcome.html",
    )


def send_email_verification(user):
    """
    Send email verification link to user
    """
    site_url = _get_site_url()
    # Generate verification token
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_verification_token.make_token(user)

    context = {
        "user": user,
        "username": user.username,
        "email": user.email,
        "uid": uid,
        "token": token,
        "verification_link": f"{site_url}/verify-email/{uid}/{token}/",
        "site_name": "Year 1 Phonics",
    }

    return send_email(
        subject="Verify Your Email - Year 1 Phonics",
        template_name="emails/email_verification.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/email_verification.html",
    )


def send_password_reset_email(user):
    """
    Send password reset email using Django's token system
    """
    site_url = _get_site_url()
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    context = {
        "user": user,
        "username": user.username,
        "email": user.email,
        "uid": uid,
        "token": token,
        "reset_link": f"{site_url}/password-reset/{uid}/{token}/",
        "site_name": "Year 1 Phonics",
    }

    return send_email(
        subject="Reset Your Password - Year 1 Phonics",
        template_name="emails/password_reset.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/password_reset.html",
    )


def send_subscription_confirmation_email(user, plan):
    """
    Send subscription confirmation email after payment
    """
    site_url = _get_site_url()
    context = {
        "user": user,
        "username": user.username,
        "plan_name": plan.name,
        "plan_price": plan.price,
        "access_years": ", ".join(str(y) for y in sorted(plan.access_years)),
        "site_name": "Year 1 Phonics",
        "dashboard_link": f"{site_url}/dashboard/",
    }

    return send_email(
        subject=f"Subscription Confirmed - {plan.name}",
        template_name="emails/subscription_confirmation.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/subscription_confirmation.html",
    )


def send_subscription_expiry_warning(user, plan, days_until_expiry):
    """
    Send warning email when subscription is about to expire
    """
    site_url = _get_site_url()
    context = {
        "user": user,
        "username": user.username,
        "plan_name": plan.name,
        "days_until_expiry": days_until_expiry,
        "renewal_link": f"{site_url}/plans/",
        "site_name": "Year 1 Phonics",
    }

    return send_email(
        subject=f"Your {plan.name} expires in {days_until_expiry} days",
        template_name="emails/subscription_expiry_warning.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/subscription_expiry_warning.html",
    )


def send_payment_failed_email(user, plan, error_message=""):
    """
    Send email when payment fails
    """
    site_url = _get_site_url()
    context = {
        "user": user,
        "username": user.username,
        "plan_name": plan.name,
        "error_message": error_message,
        "retry_link": f"{site_url}/payment/{plan.id}/",
        "site_name": "Year 1 Phonics",
    }

    return send_email(
        subject=f"Payment Failed - {plan.name}",
        template_name="emails/payment_failed.txt",
        context=context,
        recipient_list=[user.email],
        html_template="emails/payment_failed.html",
    )


def send_account_notification(
    user, subject, template_name, context, html_template=None
):
    """
    Send generic account notification email
    """
    site_url = _get_site_url()
    context.update(
        {
            "user": user,
            "username": user.username,
            "site_name": "Year 1 Phonics",
            "dashboard_link": f"{site_url}/dashboard/",
        }
    )

    return send_email(
        subject=subject,
        template_name=template_name,
        context=context,
        recipient_list=[user.email],
        html_template=html_template,
    )
