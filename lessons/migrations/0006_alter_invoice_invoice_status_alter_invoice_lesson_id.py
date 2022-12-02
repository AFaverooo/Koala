# Generated by Django 4.1.3 on 2022-12-02 00:07

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0005_alter_invoice_lesson_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='invoice_status',
            field=models.CharField(choices=[('PAID', 'This invoices has been paid'), ('UNPAID', 'This invoice has not been paid'), ('PARTIALLY_PAID', 'This invoice has been partially paid'), ('DELETED', 'This invoice has been deleted')], default='UNPAID', max_length=30),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='lesson_ID',
            field=models.CharField(blank=True, max_length=30, validators=[django.core.validators.RegexValidator(message='Lesson ID must all be number', regex='^\\d+$')]),
        ),
    ]