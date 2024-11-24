from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_subscribed:
            return view_func(request, *args, **kwargs)
        messages.warning(request, 'This feature requires a subscription.')
        return redirect('payments:checkout')
    return _wrapped_view 