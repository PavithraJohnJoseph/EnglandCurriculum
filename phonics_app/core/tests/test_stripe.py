"""
Tests for Stripe payment integration
"""

import json
import pytest
from django.test import Client
from unittest.mock import patch, MagicMock
from core.models import Subscription
from core.stripe_utils import (
    create_or_update_customer,
    create_checkout_session,
    sync_plan_with_stripe,
    handle_checkout_session_completed,
)


@pytest.mark.django_db
class TestStripeIntegration:
    """Test Stripe integration functions"""

    def test_create_or_update_customer(self):
        """Test creating a new Stripe customer"""
        from core.tests.factories import UserFactory

        user = UserFactory.create()

        with patch("core.stripe_utils.stripe.Customer.create") as mock_create:
            mock_create.return_value = MagicMock(id="cus_test123")

            customer_id = create_or_update_customer(user)

            assert customer_id == "cus_test123"
            assert user.stripe_customer_id == "cus_test123"
            mock_create.assert_called_once()

    def test_create_checkout_session(self):
        """Test creating a Stripe checkout session"""
        from core.tests.factories import UserFactory, PlanFactory

        user = UserFactory.create(stripe_customer_id="cus_test123")
        plan = PlanFactory.create(
            is_free=False, price=9.99, stripe_price_id="price_test123"
        )

        with patch("core.stripe_utils.stripe.checkout.Session.create") as mock_create:
            mock_session = MagicMock()
            mock_session.url = "https://checkout.stripe.com/pay/test123"
            mock_create.return_value = mock_session

            session = create_checkout_session(user, plan)

            assert session.url == "https://checkout.stripe.com/pay/test123"
            mock_create.assert_called_once()

    def test_create_checkout_session_free_plan_raises_error(self):
        """Test that checkout session cannot be created for free plans"""
        from core.tests.factories import UserFactory, PlanFactory

        user = UserFactory.create()
        plan = PlanFactory.create(is_free=True)

        with pytest.raises(ValueError):
            create_checkout_session(user, plan)

    def test_sync_plan_with_stripe(self):
        """Test syncing a plan with Stripe"""
        from core.tests.factories import PlanFactory

        plan = PlanFactory.create(is_free=False, stripe_price_id=None)

        with patch("core.stripe_utils.stripe.Product.create") as mock_product:
            with patch("core.stripe_utils.stripe.Price.create") as mock_price:
                mock_product.return_value = MagicMock(id="prod_test123")
                mock_price.return_value = MagicMock(id="price_test123")

                price_id = sync_plan_with_stripe(plan)

                assert price_id == "price_test123"
                plan.refresh_from_db()
                assert plan.stripe_price_id == "price_test123"

    def test_handle_checkout_session_completed(self):
        """Test handling successful checkout session"""
        from core.tests.factories import UserFactory, PlanFactory

        user = UserFactory.create()
        plan = PlanFactory.create(is_free=False)

        session_data = {
            "metadata": {"user_id": user.id, "plan_id": plan.id},
            "subscription": "sub_test123",
        }

        subscription = handle_checkout_session_completed(session_data)

        assert subscription is not None
        assert subscription.user == user
        assert subscription.plan == plan
        assert subscription.stripe_subscription_id == "sub_test123"
        assert subscription.active is True

        user.refresh_from_db()
        assert user.plan == plan


@pytest.mark.django_db
class TestPaymentViews:
    """Test payment view with Stripe"""

    def test_payment_view_free_plan_redirects(self):
        """Test that free plan redirects without payment"""
        from core.tests.factories import UserFactory, PlanFactory

        client = Client()
        user = UserFactory.create(email_verified=True)
        plan = PlanFactory.create(is_free=True)

        client.force_login(user)
        response = client.get(f"/payment/{plan.id}/")

        assert response.status_code == 302
        assert response.url == "/years/"

    def test_payment_view_paid_plan_shows_form(self):
        """Test that paid plan shows payment form"""
        from core.tests.factories import UserFactory, PlanFactory

        client = Client()
        user = UserFactory.create(email_verified=True)
        plan = PlanFactory.create(is_free=False, stripe_price_id="price_test123")

        client.force_login(user)
        response = client.get(f"/payment/{plan.id}/")

        assert response.status_code == 200
        assert b"Proceed to Secure Payment" in response.content
        assert b"Stripe" in response.content

    def test_payment_view_post_creates_checkout_session(self):
        """Test that POST creates Stripe checkout session"""
        from core.tests.factories import UserFactory, PlanFactory

        client = Client()
        user = UserFactory.create(
            stripe_customer_id="cus_test123", email_verified=True
        )
        plan = PlanFactory.create(is_free=False, stripe_price_id="price_test123")

        with patch("core.views.create_checkout_session") as mock_create:
            mock_session = MagicMock()
            mock_session.url = "https://checkout.stripe.com/pay/test123"
            mock_create.return_value = mock_session

            client.force_login(user)
            response = client.post(f"/payment/{plan.id}/")

            assert response.status_code == 302
            assert response.url == "https://checkout.stripe.com/pay/test123"


@pytest.mark.django_db
class TestStripeWebhook:
    """Test Stripe webhook handling"""

    @patch("core.views.verify_webhook_signature")
    def test_webhook_checkout_session_completed(self, mock_verify):
        """Test webhook handling for successful checkout"""
        from core.tests.factories import UserFactory, PlanFactory

        client = Client()
        user = UserFactory.create()
        plan = PlanFactory.create()

        # Mock webhook event
        webhook_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "metadata": {"user_id": str(user.id), "plan_id": str(plan.id)},
                    "subscription": "sub_test123",
                }
            },
        }

        mock_verify.return_value = webhook_data

        response = client.post(
            "/stripe-webhook/",
            data=json.dumps(webhook_data),
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )

        assert response.status_code == 200

        # Verify subscription was created
        subscription = Subscription.objects.filter(
            stripe_subscription_id="sub_test123"
        ).first()
        assert subscription is not None
        assert subscription.user == user

    @patch("core.views.verify_webhook_signature")
    def test_webhook_invalid_signature(self, mock_verify):
        """Test webhook with invalid signature"""

        client = Client()

        mock_verify.side_effect = ValueError("Invalid signature")

        response = client.post(
            "/stripe-webhook/",
            data="{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="invalid_sig",
        )

        assert response.status_code == 403
