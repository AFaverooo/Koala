# Generated by Django 4.1.3 on 2022-12-06 14:11

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import lessons.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_parent', models.BooleanField(default=False)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('PNOT', 'Prefer Not To Say')], default='PNOT', max_length=20)),
                ('role', models.CharField(choices=[('Student', 'Student'), ('Administrator', 'Admin'), ('Director', 'Director'), ('Teacher', 'Teacher')], max_length=13)),
                ('balance', models.IntegerField(blank=True, default=0, editable=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('parent_of_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='parent', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', lessons.models.UserAccountManager()),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference_number', models.CharField(max_length=30, unique=True, validators=[django.core.validators.RegexValidator(message='Reference number must all be number and consist of - in between followed by at least three numbers', regex='^\\d*\\d-\\d\\d\\d\\d*$')])),
                ('student_ID', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(message='Student ID must all be number', regex='^\\d+$')])),
                ('fees_amount', models.IntegerField(validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1)])),
                ('invoice_status', models.CharField(choices=[('PAID', 'This invoices has been paid'), ('UNPAID', 'This invoice has not been paid'), ('PARTIALLY_PAID', 'This invoice has been partially paid'), ('DELETED', 'This invoice has been deleted')], default='UNPAID', max_length=30)),
                ('amounts_need_to_pay', models.IntegerField(default=0, validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(0)])),
                ('lesson_ID', models.CharField(blank=True, max_length=30, validators=[django.core.validators.RegexValidator(message='Lesson ID must all be number', regex='^\\d+$')])),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term_number', models.IntegerField(validators=[django.core.validators.MaxValueValidator(6), django.core.validators.MinValueValidator(1)])),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Student_ID_transaction', models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(message='Student ID must all be number', regex='^\\d+$')])),
                ('invoice_reference_transaction', models.CharField(blank=True, max_length=30, validators=[django.core.validators.RegexValidator(message='Reference number must all be number and consist of - in between followed by at least three numbers', regex='^\\d*\\d-\\d\\d\\d\\d*$')])),
                ('transaction_amount', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(10000), django.core.validators.MinValueValidator(1)])),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('lesson_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('request_date', models.DateField(default=django.utils.timezone.now, verbose_name='Request Date')),
                ('type', models.CharField(choices=[('INSTR', 'Learn To Play An Instrument'), ('TH', 'Instrument Music Theory'), ('PR', 'Instrument practice'), ('PERF', 'Performance Preparation')], default='INSTR', max_length=30)),
                ('duration', models.CharField(choices=[('30', '30 minute lesson'), ('45', '45 minute lesson'), ('60', '1 hour lesson')], default='30', max_length=20)),
                ('lesson_date_time', models.DateTimeField(verbose_name='Lesson Date And Time')),
                ('lesson_status', models.CharField(choices=[('SA', 'The lesson has been saved'), ('PN', 'The lesson request is pending'), ('BK', 'The lesson has been booked')], default='SA', max_length=30)),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
                ('teacher_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('request_date', 'lesson_date_time', 'student_id')},
            },
        ),
    ]
