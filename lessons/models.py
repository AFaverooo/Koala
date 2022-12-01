from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

from django.contrib.auth.base_user import BaseUserManager

from django.utils import timezone

from django.utils.translation import gettext_lazy as _

#imports for Request
from django.conf import settings

class TransactionTypes(models.TextChoices):
    IN = 'IN', _('Student transfer money from outside into their balance')
    OUT = 'OUT', _('Student transfer money from balance into school account')

#Shows the status of the invoices
class InvoiceStatus(models.TextChoices):
    PAID = 'PAID', _('This invoices has been paid')
    UNPAID = 'UNPAID', _('This invoice has not been paid')
    PARTIALLY_PAID = 'PARTIALLY_PAID', _('This invoice has been partially paid')

class LessonStatus(models.TextChoices):
    SAVED = 'SA', _('The lesson has been saved')
    UNFULFILLED = 'PN', _('The lesson request is pending')
    FULLFILLED = 'BK', _('The lesson has been booked')
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

    balance = models.IntegerField(
        default=0,
        blank = True,
        editable=False,
        validators=[
            MaxValueValidator(10000),
        ]
    )

    def get_student_balance(self):
        return f'{self.balance}'

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

    lesson_status = models.CharField(max_length=30,choices = LessonStatus.choices, default = LessonStatus.SAVED, blank = False)

    class Meta:
        unique_together = (('request_date', 'lesson_date_time', 'student_id'),)

#Invoice refers to the invoices of the lessons student booked
class Invoice(models.Model):
    reference_number = models.CharField(
        max_length=30,
        unique=True,
        blank=False,
        validators=[RegexValidator(
            regex = r'^\d*\d-\d\d\d\d*$', 
            message='Reference number must all be number and consist of - in between followed by at least three numbers'
        )]
    )

    # student number store the student
    student_ID = models.CharField( 
        max_length = 30,
        blank=False,
        validators=[RegexValidator(
            regex = r'^\d+$', 
            message='Student ID must all be number'
        )]
    )

    fees_amount = models.IntegerField(
        blank=False,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(1),
        ]
    )

    invoice_status = models.CharField(
        max_length=30,
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.UNPAID,
        blank = False,
    )

    # this field display the amounts left need to be paid by student
    amounts_need_to_pay = models.IntegerField(
        blank=False,
        default = 0,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(0),
        ]
    )

    def generate_new_invoice_reference_number(student_id, number_of_exist_invoice):   
        #this method will be use to generate new invoice reference number base on the student reference number
        number_of_exist_invoice +=1
        if(number_of_exist_invoice < 10):
            reference_number = student_id + '-' + '00' + str(number_of_exist_invoice) # student 1 with 2 exist invoice get a new reference_number 1-003
        elif(number_of_exist_invoice < 100):
            reference_number = student_id + '-' + '0' + str(number_of_exist_invoice) # student 1 with 10 exist invoice get a new reference_number 1-011
        else:
            reference_number = student_id + '-' + str(number_of_exist_invoice) # student 1 with 788 exist invoice get a new reference_number 1-789

        return f'{reference_number}'

    def calculate_fees_amount(lessons_with_30_mins, lessons_with_45_mins, lessons_with_1_hr):
        #30 mins lesson cost 15, 45 mins lesson cost 18,  1 hr lesson cost 20, no matter the date and teacher
        fees_amount = 0
        fees_amount += len(lessons_with_30_mins)*15
        fees_amount += len(lessons_with_45_mins)*18
        fees_amount += len(lessons_with_1_hr)*20

        return f'{fees_amount}'

    def get_fees_amount(self):
        #return the total amount of fees
        return f'{self.fees_amount}'

    def change_invoice_status_to_paid(self):
        #this function change the invoice status from unpaid to paid
        self.invoice_status = InvoiceStatus.PAID

    def change_invoice_status_to_unpaid(self):
        #this function change the invoice status from paid to unpaid
        self.invoice_status = InvoiceStatus.PAID

    # def add_lesson(self, lesson_price):
    #     pass

    # def delete_lesson(self, lesson_name, lesson_price):
    #     pass
        
    def get_invoice(self):
        return (self.reference_number, self.student_ID, self.fees_amount)

class Transaction(models.Model):
    Student_ID_transaction = models.CharField( 
        max_length = 30,
        blank=False,
        validators=[RegexValidator(
            regex = r'^\d+$', 
            message='Student ID must all be number'
        )]
    )

    transaction_type = models.CharField(
        max_length=30,
        choices=TransactionTypes.choices,
        default=TransactionTypes.OUT,
        blank = False,
    )

    invoice_reference_transaction = models.CharField(
        max_length=30,
        unique=False,
        blank=True,
        validators=[RegexValidator(
            regex = r'^\d*\d-\d\d\d\d*$', 
            message='Reference number must all be number and consist of - in between followed by at least three numbers'
        )]
    )

    transaction_amount = models.IntegerField(
        blank=False,
        default= 1,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(1),
        ]
    )