from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField('email address', unique=True)
    is_subscribed = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_status = models.CharField(max_length=50, default='free')
    subscription_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.email