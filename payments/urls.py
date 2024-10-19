from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create-subscription/', views.create_subscription, name='create_subscription'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]