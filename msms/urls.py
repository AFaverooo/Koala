"""msms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from lessons import views

#Required for admin DateTimeField
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name = 'home'),
    path('jsi18n', JavaScriptCatalog.as_view(), name = 'js-catalog'),
    path('log_in/', views.log_in, name = 'log_in'),
    path('student_feed', views.student_feed, name = 'student_feed'),
    path('requests_page', views.requests_page, name = 'requests_page'),

    path('new_lesson/', views.new_lesson, name = 'new_lesson'), #adds the single lesson to the database

    path('admin_feed', views.admin_feed, name = 'admin_feed'),
    path('director_feed', views.director_feed, name = 'director_feed'),
    path('sign_up/', views.sign_up, name = 'sign_up'),
    path('log_out/', views.log_out, name = 'log_out'),
]
