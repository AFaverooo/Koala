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
    path('student_feed', views.student_feed, name = 'student_feed'),
    path('requests_page', views.requests_page, name = 'requests_page'),

    path('new_lesson/', views.new_lesson, name = 'new_lesson'), #adds the single lesson to the database
    path('save_lessons/', views.save_lessons, name = 'save_lessons'),
    path('delete_pending/<int:lesson_id>', views.delete_pending, name = 'delete_pending'), #delete single pending lesson

    #path('edit_pending/', views.edit_pending, name = 'edit_pending'),
    path('edit_lesson/<int:lesson_id>', views.edit_lesson, name = 'edit_lesson'),

    path('admin_feed', views.admin_feed, name = 'admin_feed'),
    path('director_feed', views.director_feed, name = 'director_feed'),
    path('sign_up/', views.sign_up, name = 'sign_up'),

    path('balance/', views.balance, name = 'balance'),
    path('pay_for_invoice/', views.pay_fo_invoice, name = 'pay_for_invoice'),
    path('transaction_history/', views.get_all_transactions,name='transaction_history'),
    path('invoices_history/', views.get_all_invocies, name = 'invoices_history'),
    path('student_invoices_and_transactions/<str:student_id>', views.get_student_invoices_and_transactions, name = 'student_invoices_and_transactions'),

    path('log_out/', views.log_out, name = 'log_out'),

    path('student_requests/<str:student_id>', views.student_requests, name='student_requests'),
    path('admin_update_request_page/<str:lesson_id>', views.admin_update_request_page,name='admin_update_request_page'),
    path('admin_confirm_booking/<str:lesson_id>', views.admin_confirm_booking,name='admin_confirm_booking'),
    path('admin_update_request/<str:lesson_id>', views.admin_update_request, name='admin_update_request'),
    path('delete_lesson/<str:lesson_id>', views.delete_lesson, name='delete_lesson'),
]
