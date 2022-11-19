"""Configuration of the admin interface for MSMS"""
from django.contrib import admin
from .models import UserAccount
# Register your models here.
@admin.register(UserAccount)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'first_name', 'last_name','role', 'gender' , 'is_active', 'is_staff', 'is_superuser'
    ]
