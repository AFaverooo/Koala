# Generated by Django 4.1.3 on 2022-11-23 20:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0009_invoice_student_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='student_number',
            field=models.CharField(default='', max_length=30),
        ),
    ]
