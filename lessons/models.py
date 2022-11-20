from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

from django.contrib.auth.base_user import BaseUserManager

from django.utils import timezone

from django.utils.translation import gettext as _

#imports for Request
from django.conf import settings

class UserRole(models.TextChoices):
    STUDENT = 'Student',
    ADMIN = 'Administrator',
    DIRECTOR = 'Director',

class Gender(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')
    PNOT = 'PNOT', _('Prefer Not To Say')

def is_valid_gender(Student):
    return Student.gender in {
        Gender.MALE,
        Gender.FEMALE,
        Gender.PNOT,
        }

def is_valid_role(Student):
    return Student.role in {
        UserRole.STUDENT,
        UserRole.ADMIN,
        UserRole.DIRECTOR,
        }


class StudentManager(BaseUserManager):
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

    def create_user(self, email, password, **extra_fields):
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
                'Superuser must have is_staff=True.'
            )
        if extra_fields.get('is_superuser') is not False:
            raise ValueError(
                'Superuser must have is_superuser=False.'
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



#Student model refers to the User of the MSMS application
class Student(AbstractBaseUser, PermissionsMixin):
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

    objects = StudentManager()

    gender = models.CharField(
        max_length=4,
        choices=Gender.choices,
        default=Gender.PNOT,
    )

    role = models.CharField(
        max_length=13,
        choices=UserRole.choices,
    )


class Invoice(models.Model):
    reference_number = models.CharField(
        max_length=30,
        unique=True,
    )

    fees_amount = models.IntegerField(

    )

    # list_of_lessons = models.CharField(
    #     max_length=30
    # )
    
    # list_of_price = models.CharField(
    #     max_length=30
    # )

    def add_lesson(self, lesson_name, lesson_price):
        pass


    def delete_lesson(self, lesson_name, lesson_price):
        pass
        

    def calculate_fees(self):
        pass

    def get_invoice(self):
        return (self.reference_number, self.fees_amount)


