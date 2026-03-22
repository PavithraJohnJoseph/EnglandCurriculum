"""
Tests for email system
"""

import pytest
from django.test import Client
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from core.models import User
from core.email_utils import (
    send_welcome_email,
    send_email_verification,
    send_subscription_confirmation_email,
)


@pytest.mark.django_db
class TestEmailUtilities:
    """Test email utility functions"""

    def test_send_welcome_email(self):
        """Test sending welcome email"""
        from core.tests.factories import UserFactory

        user = UserFactory.create()

        result = send_welcome_email(user)

        assert result > 0
        assert len(mail.outbox) > 0
        assert mail.outbox[-1].subject == f"Welcome to Year 1 Phonics, {user.username}!"
        assert user.email in mail.outbox[-1].to

    def test_send_email_verification(self):
        """Test sending email verification link"""
        from core.tests.factories import UserFactory

        user = UserFactory.create()

        result = send_email_verification(user)

        assert result > 0
        assert len(mail.outbox) > 0
        assert "Verify Your Email" in mail.outbox[-1].subject
        assert user.email in mail.outbox[-1].to

    def test_email_verification_link_format(self):
        """Test that verification email contains valid link format"""
        from core.tests.factories import UserFactory

        user = UserFactory.create()

        send_email_verification(user)

        email = mail.outbox[-1]
        assert (
            "verify-email" in email.body or "verify-email" in email.alternatives[0][0]
        )

    def test_send_subscription_confirmation_email(self):
        """Test sending subscription confirmation email"""
        from core.tests.factories import UserFactory, PlanFactory

        user = UserFactory.create()
        plan = PlanFactory.create(name="Gold Plan", price=9.99)

        result = send_subscription_confirmation_email(user, plan)

        assert result > 0
        assert len(mail.outbox) > 0
        assert "Gold Plan" in mail.outbox[-1].subject
        assert user.email in mail.outbox[-1].to


@pytest.mark.django_db
class TestEmailVerificationFlow:
    """Test email verification workflow"""

    def test_email_verification_with_valid_token(self):
        """Test email verification with valid token"""
        from core.tests.factories import UserFactory

        client = Client()
        user = UserFactory.create(email_verified=False)

        # Generate valid token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Verify email
        response = client.get(f"/verify-email/{uid}/{token}/")

        assert response.status_code == 200

        # Check user was marked as verified
        user.refresh_from_db()
        assert user.email_verified is True
        assert user.email_verified_at is not None

    def test_email_verification_with_invalid_token(self):
        """Test email verification with invalid token"""
        from core.tests.factories import UserFactory

        client = Client()
        user = UserFactory.create(email_verified=False)

        # Generate valid uid but invalid token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = "invalid_token_xyz"

        # Try to verify
        response = client.get(f"/verify-email/{uid}/{token}/")

        assert response.status_code == 400

        # User should not be verified
        user.refresh_from_db()
        assert user.email_verified is False

    def test_email_verification_pending_page(self):
        """Test email verification pending page"""
        from core.tests.factories import UserFactory

        client = Client()
        user = UserFactory.create(email_verified=False)

        client.force_login(user)
        response = client.get("/email-verification-pending/")

        assert response.status_code == 200
        assert user.email.encode() in response.content
        assert b"verification" in response.content.lower()


@pytest.mark.django_db
class TestSignupWithEmail:
    """Test signup flow with email sending"""

    def test_signup_sends_welcome_email(self):
        """Test that signup sends welcome email"""
        client = Client()

        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
        }

        response = client.post("/signup/", data)

        # Should redirect to email verification pending
        assert response.status_code == 302

        # Check emails were sent
        assert len(mail.outbox) >= 2  # Welcome + verification
        assert any("Welcome" in email.subject for email in mail.outbox)
        assert any("Verify" in email.subject for email in mail.outbox)

    def test_signup_creates_unverified_user(self):
        """Test that new signup creates unverified user"""
        client = Client()

        data = {
            "username": "newuser2",
            "email": "newuser2@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
        }

        client.post("/signup/", data)

        # Check user was created
        user = User.objects.get(username="newuser2")
        assert user.email_verified is False
        assert user.email_verified_at is None

    def test_signup_redirects_to_verification_pending(self):
        """Test that signup redirects to verification pending page"""
        client = Client()

        data = {
            "username": "newuser3",
            "email": "newuser3@example.com",
            "password1": "SecurePassword123!",
            "password2": "SecurePassword123!",
        }

        response = client.post("/signup/", data, follow=True)

        # Should end up at email verification pending
        assert response.status_code == 200
        assert (
            b"email-verification-pending" in response.content
            or b"Verify Your Email" in response.content
        )


@pytest.mark.django_db
class TestEmailInStripeWebhook:
    """Test that emails are sent during Stripe webhook events"""

    def test_stripe_webhook_sends_confirmation_email(self):
        """Test that Stripe webhook sends subscription confirmation"""
        from core.tests.factories import UserFactory, PlanFactory
        from unittest.mock import patch
        import json

        client = Client()
        user = UserFactory.create()
        plan = PlanFactory.create()

        webhook_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"user_id": str(user.id), "plan_id": str(plan.id)},
                    "subscription": "sub_test123",
                }
            },
        }

        with patch("core.views.verify_webhook_signature") as mock_verify:
            mock_verify.return_value = webhook_data

            response = client.post(
                "/stripe-webhook/",
                data=json.dumps(webhook_data),
                content_type="application/json",
                HTTP_STRIPE_SIGNATURE="test_sig",
            )

            assert response.status_code == 200

            # Check confirmation email was sent
            assert len(mail.outbox) > 0
            assert any(
                "Subscription Confirmed" in email.subject for email in mail.outbox
            )
