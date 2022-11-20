"""Configuration of the admin interface for MSMS"""
from django.contrib import admin
from .models import Student, Invoice
# Register your models here.
@admin.register(Student)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name','role', 'gender' , 'is_active', 'is_staff', 'is_superuser'
    ]

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['reference_number','fees_amount'
    ]

