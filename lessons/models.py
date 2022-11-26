from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

from django.contrib.auth.base_user import BaseUserManager

from django.utils import timezone

from django.utils.translation import gettext_lazy as _

#imports for Request
from django.conf import settings

class LessonStatus(models.TextChoices):
    SAVED = 'SA', _('The lesson has been saved')
    PENDING = 'PN', _('The lesson request is pending')
    BOOKED = 'BK', _('The lesson has been booked')
#test fot lesson type
class LessonType(models.TextChoices):
    INSTRUMENT = 'INSTR', _('Learn To Play An Instrument'),
    THEORY = 'TH', _('Instrument Music Theory'),
    PRACTICE = 'PR', _('Instrument practice'),
    PERFORMANCE = 'PERF', _('Performance Preparation'),

    #def getType(self):
    #    return f'{self.label}'

#test for lesson duration
class LessonDuration(models.TextChoices):
    THIRTY = '30', _('30 minute lesson')
    FOURTY_FIVE = '45', _('45 minute lesson')
    HOUR = '60', _('1 hour lesson')

    #def getDuration(self):
    #    return f'{self.label}'

    #def getLabel(self):
    #    return f'{self.label}'

#added a teacher as a user role
class UserRole(models.TextChoices):
    STUDENT = 'Student'
    ADMIN = 'Administrator'
    DIRECTOR = 'Director'
    TEACHER = 'Teacher'

    def is_student(self):
        return self.value == 'Student'


class Gender(models.TextChoices):
    MALE = 'M' , _('Male')
    FEMALE = 'F', _('Female')
    PNOT = 'PNOT', _('Prefer Not To Say')


class UserAccountManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        '''Create and save a student with the given email, and
        password without a username
        '''
        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_student(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.STUDENT)
        return self._create_user(email, password, **extra_fields)

    def create_admin(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', UserRole.ADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Admin must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not False:
            raise ValueError(
                'Admin must have is_superuser=False.'
            )

        return self._create_user(email, password, **extra_fields)

    def create_teacher(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', UserRole.TEACHER)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Teacher must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not False:
            raise ValueError(
                'Teacher must have is_superuser=False.'
            )

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.DIRECTOR)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must have is_superuser=True.'
            )

        return self._create_user(email, password, **extra_fields)

#UserAccount model refers to the User of the MSMS application
class UserAccount(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)

    is_staff = models.BooleanField(
        default=False,
        help_text=(
            'Designates whether the user can log into '
            'this admin site.'
        ),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=(
            'Designates whether this user should be '
            'treated as active. Unselect this instead '
            'of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(
        default=timezone.now,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserAccountManager()

    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        default=Gender.PNOT,
    )

    role = models.CharField(
        max_length=13,
        choices=UserRole.choices,
    )

    def get_student_id(self):
        return f'{self.id}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Lesson(models.Model):
    lesson_id = models.BigAutoField(primary_key=True)

    request_date = models.DateField('Request Date And Time', default=timezone.now)

    type = models.CharField(
        max_length=30,
        choices=LessonType.choices,
        default=LessonType.INSTRUMENT,
        blank = False
    )

    duration = models.CharField(
        max_length = 20,
        choices = LessonDuration.choices,
        default = LessonDuration.THIRTY,
        blank = False
    )

    lesson_date_time = models.DateTimeField('Lesson Date And Time')

    teacher_id = models.ForeignKey(UserAccount,on_delete=models.CASCADE, related_name = 'teacher')

    student_id = models.ForeignKey(UserAccount, on_delete = models.CASCADE, related_name = 'student')

    is_booked = models.CharField(max_length=30,choices = LessonStatus.choices, default = LessonStatus.SAVED, blank = False)

    class Meta:
        unique_together = (('request_date', 'lesson_date_time', 'student_id'),)
