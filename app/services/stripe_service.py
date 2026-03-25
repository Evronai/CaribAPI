import stripe
from typing import Optional
from app.config import settings

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key

def create_stripe_customer(
    email: str,
    name: Optional[str] = None,
    payment_method_id: Optional[str] = None
) -> stripe.Customer:
    """
    Create a new Stripe customer
    """
    customer_data = {
        "email": email,
        "name": name,
        "metadata": {
            "service": "CaribAPI",
            "plan": "free"
        }
    }
    
    customer = stripe.Customer.create(**customer_data)
    
    # Attach payment method if provided
    if payment_method_id:
        try:
            # Attach payment method to customer
            stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer.id
            )
            
            # Set as default payment method
            stripe.Customer.modify(
                customer.id,
                invoice_settings={
                    "default_payment_method": payment_method_id
                }
            )
        except stripe.error.StripeError as e:
            # Log error but don't fail customer creation
            print(f"Warning: Failed to attach payment method: {str(e)}")
    
    return customer

def create_subscription(
    customer_id: str,
    price_id: str,
    payment_method_id: Optional[str] = None
) -> stripe.Subscription:
    """
    Create a subscription for a customer
    """
    subscription_data = {
        "customer": customer_id,
        "items": [{"price": price_id}],
        "payment_behavior": "default_incomplete",
        "expand": ["latest_invoice.payment_intent"],
        "metadata": {
            "service": "CaribAPI"
        }
    }
    
    # If payment method provided, add it
    if payment_method_id:
        subscription_data["default_payment_method"] = payment_method_id
    
    subscription = stripe.Subscription.create(**subscription_data)
    
    return subscription

def cancel_subscription(subscription_id: str) -> stripe.Subscription:
    """
    Cancel a subscription
    """
    subscription = stripe.Subscription.delete(subscription_id)
    return subscription

def get_subscription(subscription_id: str) -> stripe.Subscription:
    """
    Get subscription details
    """
    subscription = stripe.Subscription.retrieve(subscription_id)
    return subscription

def update_subscription_plan(
    subscription_id: str,
    new_price_id: str
) -> stripe.Subscription:
    """
    Update subscription to a new plan
    """
    subscription = stripe.Subscription.retrieve(subscription_id)
    
    # Update subscription items
    updated_subscription = stripe.Subscription.modify(
        subscription_id,
        items=[{
            "id": subscription["items"]["data"][0].id,
            "price": new_price_id
        }],
        proration_behavior="create_prorations"
    )
    
    return updated_subscription

def create_checkout_session(
    customer_id: str,
    price_id: str,
    success_url: str,
    cancel_url: str
) -> stripe.checkout.Session:
    """
    Create a checkout session for subscription
    """
    session = stripe.checkout.Session.create(
        customer=customer_id,
        payment_method_types=["card"],
        line_items=[{
            "price": price_id,
            "quantity": 1,
        }],
        mode="subscription",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "service": "CaribAPI"
        }
    )
    
    return session

def handle_webhook(payload: bytes, sig_header: str) -> dict:
    """
    Handle Stripe webhook events
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e
    
    # Handle different event types
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    # Map of event handlers
    event_handlers = {
        "customer.subscription.created": handle_subscription_created,
        "customer.subscription.updated": handle_subscription_updated,
        "customer.subscription.deleted": handle_subscription_deleted,
        "invoice.payment_succeeded": handle_payment_succeeded,
        "invoice.payment_failed": handle_payment_failed,
    }
    
    # Call appropriate handler
    if event_type in event_handlers:
        event_handlers[event_type](event_data)
    
    return {"status": "success", "event": event_type}

def handle_subscription_created(subscription: dict):
    """
    Handle new subscription creation
    """
    # Update user plan in database
    # This would typically update your database
    print(f"New subscription created: {subscription['id']}")

def handle_subscription_updated(subscription: dict):
    """
    Handle subscription updates
    """
    print(f"Subscription updated: {subscription['id']}")

def handle_subscription_deleted(subscription: dict):
    """
    Handle subscription cancellation
    """
    # Downgrade user to free plan
    print(f"Subscription deleted: {subscription['id']}")

def handle_payment_succeeded(invoice: dict):
    """
    Handle successful payment
    """
    print(f"Payment succeeded for invoice: {invoice['id']}")

def handle_payment_failed(invoice: dict):
    """
    Handle failed payment
    """
    print(f"Payment failed for invoice: {invoice['id']}")