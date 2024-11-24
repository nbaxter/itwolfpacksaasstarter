import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect
from .models import Subscription
import json
from datetime import datetime, timezone

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def checkout(request):
    return render(request, 'payments/checkout.html', {
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY
    })

@login_required
@require_POST
def create_subscription(request):
    try:
        # Create or get Stripe customer
        if request.user.stripe_customer_id:
            customer = stripe.Customer.retrieve(request.user.stripe_customer_id)
        else:
            customer = stripe.Customer.create(
                email=request.user.email,
                metadata={'user_id': request.user.id}
            )
            request.user.stripe_customer_id = customer.id
            request.user.save()

        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer.id,
            payment_method_types=['card'],
            line_items=[{
                'price': 'price_YOUR_PRICE_ID',  # Replace with your Stripe price ID
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.build_absolute_uri('/payments/success/'),
            cancel_url=request.build_absolute_uri('/payments/checkout/'),
        )
        
        return JsonResponse({'id': checkout_session.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status=400)

    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event)
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event)
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event)

    return HttpResponse(status=200)

def handle_subscription_created(event):
    subscription = event['data']['object']
    user = CustomUser.objects.get(stripe_customer_id=subscription['customer'])
    
    # Update user subscription status
    user.is_subscribed = True
    user.subscription_status = subscription['status']
    user.subscription_id = subscription['id']
    user.save()

    # Create subscription record
    Subscription.objects.create(
        user=user,
        stripe_subscription_id=subscription['id'],
        status=subscription['status'],
        current_period_end=datetime.fromtimestamp(subscription['current_period_end'], timezone.utc)
    )

def handle_subscription_updated(event):
    subscription = event['data']['object']
    user = CustomUser.objects.get(stripe_customer_id=subscription['customer'])
    
    # Update user subscription status
    user.subscription_status = subscription['status']
    user.save()

    # Update subscription record
    sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
    sub.status = subscription['status']
    sub.current_period_end = datetime.fromtimestamp(subscription['current_period_end'], timezone.utc)
    sub.save()

def handle_subscription_deleted(event):
    subscription = event['data']['object']
    user = CustomUser.objects.get(stripe_customer_id=subscription['customer'])
    
    # Update user subscription status
    user.is_subscribed = False
    user.subscription_status = 'canceled'
    user.save()

    # Update subscription record
    sub = Subscription.objects.get(stripe_subscription_id=subscription['id'])
    sub.status = 'canceled'
    sub.save()

@login_required
def success(request):
    return render(request, 'payments/success.html')