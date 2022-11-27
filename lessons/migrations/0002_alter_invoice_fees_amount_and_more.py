# Generated by Django 4.1.3 on 2022-11-27 23:42

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='fees_amount',
            field=models.IntegerField(validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='reference_number',
            field=models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Reference number must all be number and consist of - in between followed by at least three numbers', regex='^\\d*\\d-\\d\\d\\d\\d*$')]),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='student_ID',
            field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(message='Student ID must all be number', regex='^\\d+$')]),
        ),
    ]
