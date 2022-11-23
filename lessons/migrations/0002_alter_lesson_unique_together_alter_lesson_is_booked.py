# Generated by Django 4.1.3 on 2022-11-23 22:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='lesson',
            unique_together={('request_date', 'lesson_date_time', 'student_id')},
        ),
        migrations.AlterField(
            model_name='lesson',
            name='is_booked',
            field=models.CharField(choices=[('SA', 'The lesson has not been saved'), ('PN', 'The lesson request is pending'), ('BK', 'The lesson has been booked')], default='SA', max_length=30),
        ),
    ]
