from django.shortcuts import render
from payments.decorators import subscription_required
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'index.html')

@login_required
@subscription_required
def premium_feature(request):
    return render(request, 'premium_feature.html')
