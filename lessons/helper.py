from django.conf import settings
from django.shortcuts import redirect
from .models import UserRole, Term


# Ensures user must log in before logging out (and redirects specific roles to their home page)

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if (request.user.role == UserRole.STUDENT.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_STUDENT)
            elif (request.user.role == UserRole.ADMIN.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_ADMIN)
            elif (request.user.role == UserRole.DIRECTOR.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_DIRECTOR)
        else:
            return view_function(request)
    return modified_view_function




def check_valid_date(lesson_date):
    term_six_date = Term.objects.get(term_number = 6).end_date
    return lesson_date <= term_six_date
