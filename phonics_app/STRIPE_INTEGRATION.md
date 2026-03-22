# Stripe Integration Guide

## Overview

Your phonics app now has full Stripe integration for processing customer payments and managing recurring subscriptions. This guide covers setup, usage, and troubleshooting.

## Architecture

The Stripe integration consists of several components:

### 1. **Stripe Utilities** (`core/stripe_utils.py`)
Core functions for Stripe operations:
- `create_or_update_customer()` - Create Stripe customer or retrieve existing
- `create_checkout_session()` - Create checkout session for payment
- `sync_plan_with_stripe()` - Create/update Stripe products and prices
- `handle_checkout_session_completed()` - Process successful payment
- `handle_customer_subscription_deleted()` - Handle subscription cancellation
- `handle_invoice_payment_failed()` - Handle failed payments
- `verify_webhook_signature()` - Verify webhook authenticity

### 2. **Payment Flow**
```
User selects paid plan → payment view → Stripe checkout session created 
→ User redirected to Stripe Checkout → Payment completed → 
Webhook received → Subscription created in database → User redirected to app
```

### 3. **Webhook Handler** (`core/views.py::stripe_webhook`)
Handles real-time events from Stripe:
- `checkout.session.completed` - Payment successful
- `customer.subscription.deleted` - Subscription cancelled
- `invoice.payment_failed` - Payment failed

## Setup Instructions

### 1. Install Dependencies
Stripe is already in `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 2. Get Stripe Keys

1. Go to [https://stripe.com/dashboard](https://stripe.com/dashboard)
2. Sign up or log in
3. Navigate to **Developers → API Keys**
4. Get your:
   - Publishable Key (`pk_test_...`)
   - Secret Key (`sk_test_...`)

### 3. Configure Environment Variables

Create/update `.env` file:

```bash
# Stripe Configuration
STRIPE_PUBLIC_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_SECRET_HERE

# Stripe Callback URLs
STRIPE_CALLBACK_SUCCESS_URL=http://localhost:8000/years/
STRIPE_CALLBACK_CANCEL_URL=http://localhost:8000/plans/

# Production URLs
# STRIPE_CALLBACK_SUCCESS_URL=https://yourdomain.com/years/
# STRIPE_CALLBACK_CANCEL_URL=https://yourdomain.com/plans/
```

### 4. Sync Plans with Stripe

Create Stripe products and prices for all plans in your database:

```bash
python manage.py sync_plans_with_stripe
```

Output:
```
✓ Bronze Plan: Already synced (stripe_price_id=price_xxx)
✓ Silver Plan: Synced (price_id=price_yyy)
✓ Gold Plan: Synced (price_id=price_zzz)

==================================================
✓ Synced: 2
⊘ Skipped: 1
✗ Errors: 0
```

**Force re-sync all plans:**
```bash
python manage.py sync_plans_with_stripe --force
```

### 5. Set Up Webhook Endpoint

Stripe needs to notify your app of events.

#### Local Development (using ngrok or Stripe CLI):

1. Install [Stripe CLI](http://stripe.com/docs/stripe-cli):
   ```bash
   stripe login
   ```

2. Forward events to your local server:
   ```bash
   stripe listen --forward-to localhost:8000/stripe-webhook/
   ```

3. This will output a webhook signing secret - add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_test_YOUR_SECRET_FROM_CLI
   ```

#### Production Deployment:

1. Go to Stripe Dashboard → **Developers → Webhooks**
2. Click **Add Endpoint**
3. Set Endpoint URL: `https://yourdomain.com/stripe-webhook/`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.deleted`
   - `invoice.payment_failed`
5. Copy the Signing Secret and add to `.env.production`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_PRODUCTION_SECRET
   ```

## Usage Flow

### Customer Payment Process

1. **User selects plan:**
   - Clicks "Silver Plan" or "Gold Plan"
   - Redirected to payment page

2. **Payment page loads:**
   - Shows plan details and pricing
   - Displays "Proceed to Secure Payment" button
   - Powered by Stripe integration

3. **User clicks payment button:**
   - Backend creates Stripe Checkout Session
   - User redirected to Stripe's secure checkout page
   - User enters card details

4. **Payment processed:**
   - Stripe processes payment
   - On success: Customer redirected to `/years/` on your app
   - On cancel: Customer redirected to `/plans/`

5. **Webhook confirmation:**
   - Stripe sends `checkout.session.completed` event
   - App receives webhook and creates `Subscription` record
   - User's plan is updated in database

### Database Records Created

When payment succeeds, these are created/updated:

**User model:**
- `plan` - Updated to selected plan
- `stripe_customer_id` - Stripe customer ID (created once)

**Subscription model:**
```
user: <User>
plan: <Plan>
start_date: <Today>
end_date: <1 year from today>
active: True
stripe_subscription_id: <Stripe subscription ID>
```

## Testing

### Run Stripe Tests

```bash
pytest core/tests/test_stripe.py -v
```

All tests use mocks, so no real Stripe API calls are made.

### Test Card Numbers

Use these cards in Stripe test mode:

| Card | Number | CVC | Expiry |
|------|--------|-----|--------|
| Visa | 4242 4242 4242 4242 | Any | Any future date |
| Visa (incorrect) | 4000 0000 0000 0002 | Any | Any future date |
| Amex | 3782 822463 10005 | Any | Any future date |

### Manual Testing Checklist

- [ ] Free plan redirects without payment
- [ ] Paid plan shows Stripe checkout button
- [ ] Clicking button redirects to Stripe Checkout
- [ ] Stripe webhook receives payment confirmation
- [ ] User subscription is created in database
- [ ] `Subscription.active` is True
- [ ] `Subscription.is_valid()` returns True
- [ ] Access control middleware grants access
- [ ] User can see years according to plan
- [ ] Failing card shows error message

## Troubleshooting

### "Failed to initiate payment: ..."

**Check:**
1. Stripe keys in `.env` are correct
2. Plan has `stripe_price_id` set
3. Run: `python manage.py sync_plans_with_stripe`

### Webhook not receiving events

**Development:**
1. Is Stripe CLI running? `stripe listen --forward-to localhost:8000/stripe-webhook/`
2. Check webhook secret in `.env` matches CLI output
3. View events: `stripe logs tail`

**Production:**
1. Verify endpoint in Stripe Dashboard → Webhooks
2. Check that HTTPS is enabled
3. Verify `STRIPE_WEBHOOK_SECRET` in environment
4. Check server logs for webhook errors

### Payment successful but subscription not created

**Check:**
1. Webhook endpoint exists at `/stripe-webhook/`
2. Webhook signature verification passes
3. User and Plan IDs in webhook metadata are correct
4. Database migration for Subscription model ran

**Debug:**
```bash
# Check webhook events in Stripe Dashboard
# View server logs for errors
docker logs <container-id>
```

### "Invalid webhook signature"

1. Verify `STRIPE_WEBHOOK_SECRET` is correct
2. Regenerate webhook secret in Stripe Dashboard if needed
3. Update local `.env` with new secret

## Important Notes

### Security

✅ **What's secure:**
- Webhook signatures verified before processing
- Card details never touch your servers (Stripe handles it)
- CSRF tokens on all payment forms
- SSL/TLS required for production

⚠️ **What you must do:**
- Rotate `STRIPE_SECRET_KEY` regularly
- Never commit real Stripe keys to git (use `.env`)
- Use HTTPS in production
- Update webhook secret if compromised

### Subscription Management

**Current behavior:**
- Auto-renews every year
- Payment fails → subscription marked inactive
- No manual cancellation UI yet (can do via dashboard)

**To implement cancellation UI:**
- Add customer portal link
- Or create cancel subscription endpoint using `stripe.Subscription.delete()`

### Monitoring

**Track payments:**
1. Stripe Dashboard → **Payments** - See all transactions
2. Check `Subscription` model for active subscriptions
3. Monitor webhook logs

**Logs in production:**
```bash
# Check app logs
docker logs phonics_web

# Check if webhook errors appear
grep "stripe" /var/log/phonics/app.log
```

## Next Steps

1. ✅ Test in test mode with Stripe test cards
2. ✅ Deploy to production when ready
3. ✅ Switch to live keys (remove `_test` from keys)
4. ✅ Configure production webhook endpoint
5. ⏳ (Future) Add customer portal for subscription management
6. ⏳ (Future) Add manual invoice handling
7. ⏳ (Future) Add refund processing

## File Reference

| File | Purpose |
|------|---------|
| `core/stripe_utils.py` | Stripe utility functions |
| `core/views.py` | Payment and webhook views |
| `core/urls.py` | Webhook URL routing |
| `core/templates/core/payment.html` | Payment page UI |
| `core/management/commands/sync_plans_with_stripe.py` | Plan sync command |
| `core/tests/test_stripe.py` | Stripe tests |
| `.env.example` | Environment keys template |

## Support

For issues:
1. Check Stripe Dashboard → Logs
2. Review app logs: `docker logs <container>`
3. Test webhook: `stripe trigger payment_intent.succeeded`
4. Contact Stripe support at [https://support.stripe.com](https://support.stripe.com)
