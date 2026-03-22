"""
Stripe integration utilities for handling payments and subscriptions
"""

import stripe
from django.conf import settings
from typing import Optional

# Initialize Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_or_update_customer(user) -> Optional[str]:
    """
    Create a Stripe customer for a user, or return existing customer ID
    """
    if user.stripe_customer_id:
        # Customer already exists
        return user.stripe_customer_id

    try:
        customer = stripe.Customer.create(
            email=user.email, name=user.username, metadata={"user_id": user.id}
        )
        user.stripe_customer_id = customer.id
        user.save()
        return customer.id
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create Stripe customer: {str(e)}")


def create_checkout_session(user, plan) -> str:
    """
    Create a Stripe Checkout Session for a plan purchase
    Returns the checkout session and redirect URL
    """
    if plan.is_free:
        raise ValueError("Cannot create checkout session for free plan")

    try:
        # Get or create Stripe customer
        customer_id = create_or_update_customer(user)

        # Ensure we always send a valid Stripe line item.
        line_item = None

        if plan.stripe_price_id:
            line_item = {
                "price": plan.stripe_price_id,
                "quantity": 1,
            }
        else:
            # Try to create/sync a reusable Stripe Price first.
            try:
                synced_price_id = sync_plan_with_stripe(plan)
                if synced_price_id:
                    line_item = {
                        "price": synced_price_id,
                        "quantity": 1,
                    }
            except Exception:
                # Fallback to inline price_data so checkout can still proceed.
                line_item = {
                    "price_data": {
                        "currency": "gbp",
                        "unit_amount": int(plan.price * 100),
                        "recurring": {"interval": "year", "interval_count": 1},
                        "product_data": {
                            "name": plan.name,
                            "metadata": {
                                "plan_id": str(plan.id),
                                "years": ",".join(
                                    str(y) for y in (plan.access_years or [])
                                ),
                            },
                        },
                    },
                    "quantity": 1,
                }

        separator = "&" if "?" in settings.STRIPE_CALLBACK_SUCCESS_URL else "?"
        success_url = (
            f"{settings.STRIPE_CALLBACK_SUCCESS_URL}"
            f"{separator}session_id={{CHECKOUT_SESSION_ID}}"
        )

        session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=["card"],
            line_items=[line_item],
            mode="subscription",
            success_url=success_url,
            cancel_url=settings.STRIPE_CALLBACK_CANCEL_URL,
            metadata={"user_id": user.id, "plan_id": plan.id, "plan_name": plan.name},
        )

        return session
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to create checkout session: {str(e)}")


def sync_plan_with_stripe(plan):
    """
    Create or update a Stripe price for a plan
    Updates the plan's stripe_price_id
    """
    try:
        if not plan.stripe_price_id:
            # Create product first
            product = stripe.Product.create(
                name=plan.name,
                metadata={
                    "plan_id": plan.id,
                    "years": ",".join(str(y) for y in plan.access_years),
                },
            )

            # Create recurring price
            price = stripe.Price.create(
                product=product.id,
                currency="gbp",
                unit_amount=int(plan.price * 100),  # Convert to pence
                recurring={"interval": "year", "interval_count": 1},
                metadata={"plan_id": plan.id},
            )

            plan.stripe_price_id = price.id
            plan.save()

        return plan.stripe_price_id
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to sync plan with Stripe: {str(e)}")


def handle_checkout_session_completed(session_data):
    """
    Handle successful checkout session completion
    Creates subscription and updates user plan
    """
    from .models import User, Plan, Subscription
    from django.utils import timezone
    from datetime import timedelta

    try:
        user_id = session_data.get("metadata", {}).get("user_id")
        plan_id = session_data.get("metadata", {}).get("plan_id")
        subscription_id = session_data.get("subscription")

        if not user_id or not plan_id:
            raise ValueError("Missing user_id or plan_id in session metadata")

        user = User.objects.get(id=user_id)
        plan = Plan.objects.get(id=plan_id)

        # Update user's plan
        user.plan = plan
        user.save()

        # Create or update subscription record
        subscription, created = Subscription.objects.update_or_create(
            user=user,
            plan=plan,
            defaults={
                "stripe_subscription_id": subscription_id,
                "active": True,
                "end_date": timezone.now().date() + timedelta(days=365),
            },
        )

        return subscription
    except Exception as e:
        raise Exception(f"Failed to handle checkout completion: {str(e)}")


def handle_customer_subscription_deleted(subscription_data):
    """
    Handle subscription cancellation from Stripe
    Marks subscription as inactive
    """
    from .models import Subscription

    try:
        stripe_subscription_id = subscription_data.get("id")

        subscription = Subscription.objects.filter(
            stripe_subscription_id=stripe_subscription_id
        ).first()

        if subscription:
            subscription.active = False
            subscription.save()
            return subscription

        return None
    except Exception as e:
        raise Exception(f"Failed to handle subscription deletion: {str(e)}")


def handle_invoice_payment_failed(invoice_data):
    """
    Handle failed payment from Stripe
    Marks subscription as inactive
    """
    from .models import Subscription

    try:
        subscription_id = invoice_data.get("subscription")

        subscription = Subscription.objects.filter(
            stripe_subscription_id=subscription_id
        ).first()

        if subscription:
            subscription.active = False
            subscription.save()
            return subscription

        return None
    except Exception as e:
        raise Exception(f"Failed to handle payment failure: {str(e)}")


def verify_webhook_signature(body, sig_header):
    """
    Verify that the webhook came from Stripe
    """
    try:
        event = stripe.Webhook.construct_event(
            body, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return event
    except stripe.error.SignatureVerificationError:
        raise ValueError("Invalid webhook signature")
    except Exception as e:
        raise Exception(f"Webhook verification failed: {str(e)}")


def finalize_checkout_from_session_id(user, session_id):
    """
    Finalize checkout from a Stripe Checkout session id on success return.
    This is a fallback path when webhook delivery is delayed.
    """
    try:
        session = stripe.checkout.Session.retrieve(session_id)

        if not session:
            raise ValueError("Checkout session not found")

        metadata = session.get("metadata") or {}
        metadata_user_id = str(metadata.get("user_id", ""))
        if metadata_user_id and metadata_user_id != str(user.id):
            raise ValueError("Checkout session does not belong to current user")

        if session.get("payment_status") != "paid":
            raise ValueError("Checkout session is not paid")

        return handle_checkout_session_completed(session)
    except stripe.error.StripeError as e:
        raise Exception(f"Failed to finalize checkout session: {str(e)}")
