# Generated by Django 4.1.3 on 2022-11-14 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0004_alter_student_options_alter_student_managers_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('P', 'Prefer Not To Say')], default='P', max_length=1),
        ),
    ]
