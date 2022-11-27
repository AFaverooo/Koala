from django.conf import settings
from django.shortcuts import redirect


# Decorator
def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
        # modified view modified_view_function
    return modified_view_function
