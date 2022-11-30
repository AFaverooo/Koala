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
    path('save_lessons/', views.save_lessons, name = 'save_lessons'),

    path('admin_feed', views.admin_feed, name = 'admin_feed'),

    path('director_manage_roles', views.director_manage_roles, name = 'director_manage_roles'),
    path('director_feed', views.director_feed, name = 'director_feed'),
    path('promote_director/<str:current_user_email>', views.promote_director, name = 'promote_director'),
    path('promote_admin/<str:current_user_email>', views.promote_admin, name = 'promote_admin'),
    path('promote_teacher/<str:current_user_email>', views.promote_teacher, name = 'promote_teacher'),
    path('promote_student/<str:current_user_email>', views.promote_student, name = 'promote_student'),
    path('edit_user/<str:current_user_email>', views.edit_user, name = 'edit_user'),
    path('disable_user/<str:current_user_email>', views.disable_user, name = 'disable_user'),
    path('delete_user/<str:current_user_email>', views.delete_user, name = 'delete_user'),
    path('create_admin_page', views.create_admin_page, name = 'create_admin_page'),

    path('sign_up/', views.sign_up, name = 'sign_up'),

    path('invoice/', views.invoice, name = 'invoice'),
    path('log_out/', views.log_out, name = 'log_out'),

    path('student_requests/<str:student>', views.get_student_lessons, name="student_requests"),
    path('update_request/<str:id>', views.update_request,name='update_request'),
    path('confirm_booking/<str:current_lesson_id>', views.confirm_booking,name='confirm_booking')
]
