import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import render, redirect

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
        # Create customer if doesn't exist
        if not request.user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=request.user.email,
                source=request.POST['stripeToken']
            )
            request.user.stripe_customer_id = customer.id
            request.user.save()

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=request.user.stripe_customer_id,
            items=[{'price': 'your-price-id'}],  # Replace with your price ID
            expand=['latest_invoice.payment_intent']
        )

        return JsonResponse({
            'subscription_id': subscription.id,
            'client_secret': subscription.latest_invoice.payment_intent.client_secret
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        user = CustomUser.objects.get(stripe_customer_id=subscription.customer)
        user.subscription_status = subscription.status
        user.save()

    return HttpResponse(status=200)