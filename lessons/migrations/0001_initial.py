from django.conf import settings
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
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('PNOT', 'Prefer Not To Say')], default='PNOT', max_length=20)),
                ('role', models.CharField(choices=[('UserAccount', 'Student'), ('Administrator', 'Admin'), ('Director', 'Director'), ('Teacher', 'Teacher')], max_length=13)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
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
            name='groupLessons',
            fields=[
                ('group_id', models.BigAutoField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='requests',
            fields=[
                ('request_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date_request_made', models.DateField(default=django.utils.timezone.now)),
                ('is_booking', models.BooleanField(default=False, help_text='Designates whether the request has been booked')),
                ('groupLessons_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.grouplessons')),
                ('student_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('lesson_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(choices=[('Learn To Play An Instrument', 'Instrument'), ('Instrument Music Theory', 'Theory'), ('Instrument practice', 'Practice'), ('Performance Preparation', 'Performance')], default='Learn To Play An Instrument', max_length=30)),
                ('duration', models.CharField(choices=[('30', '30 minute lesson'), ('45', '45 minute lesson'), ('60', '1 hour lesson')], default='30', max_length=20)),
                ('lesson_date_time', models.DateTimeField(verbose_name='Lesson Date And Time')),
                ('teacher_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='grouplessons',
            name='lesson_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lessons.lesson'),
        ),
    ]
