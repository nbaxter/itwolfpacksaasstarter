from django.db import models
from django.conf import settings

class StripeCustomer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    current_period_end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)