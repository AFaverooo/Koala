"""Configuration of the admin interface for MSMS"""
from django.contrib import admin
from .models import UserAccount,Lesson, Invoice, Transaction
# Register your models here.
@admin.register(UserAccount)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id','email', 'first_name', 'last_name','role', 'gender' , 'balance', 'is_active', 'is_staff', 'is_superuser'
    ]

@admin.register(Lesson)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'lesson_id', 'request_date' ,'type', 'duration' , 'lesson_date_time', 'teacher_id', 'student_id', 'lesson_status'
    ]

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['reference_number','student_ID','fees_amount', 'invoice_status'
    ]

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['Student_ID_transaction', 'transaction_type', 'invoice_reference_transaction', 'transaction_amount'
    ]
