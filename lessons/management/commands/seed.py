from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus,Invoice, InvoiceStatus, Transaction, TransactionTypes
import random
import string
import datetime
from django.utils import timezone


letters = string.ascii_lowercase

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.faker = Faker('en_GB')

    # Seeds the database with users
    def handle(self, *args, **options):

        # Add the set Student, Admin and Directors
        self.student = UserAccount.objects.create_student(
            first_name="John",
            last_name="Doe",
            email= "john.doe@example.org",
            password="Password123",
            gender ="M",
        )
        self.student = UserAccount.objects.create_admin(
            first_name="Petra",
            last_name="Pickles",
            email= "petra.pickles@example.org",
            password="Password123",
            gender ="F",
        )
        self.student = UserAccount.objects.create_superuser(
            first_name="Marty",
            last_name="Major",
            email= "marty.major@example.org",
            password="Password123",
            gender ="PNOT",
        )

        # Seed the students
        for i in range(99):

            fname = self.faker.unique.first_name()
            lname = self.faker.unique.last_name()
            mails = ["gmail.com","yahoo.com","outlook.com","example.org"]
            random_password = ''.join(random.choice(letters) for i in range(10))
            genders = ['M','F','PNOT']

            self.student = UserAccount.objects.create_student(
                first_name=fname,
                last_name=lname,
                email= f'{fname[0].lower()}{lname.lower()}{random.randint(0,100)}@{mails[random.randint(0,3)]}',
                password=f'{random_password}',
                gender = f'{genders[random.randint(0,2)]}',
            )



        # Seed the teachers
        for i in range(5):

            fname = self.faker.unique.first_name()
            lname = self.faker.unique.last_name()
            mails = ["gmail.com","yahoo.com","outlook.com","example.org"]
            random_password = ''.join(random.choice(letters) for i in range(10))
            genders = ['M','F','PNOT']
            
            self.student = UserAccount.objects.create_teacher(
                first_name=fname,
                last_name=lname,
                email= f'{fname[0].lower()}{lname.lower()}{random.randint(0,100)}@{mails[random.randint(0,3)]}',
                password=f'{random_password}',
                gender = f'{genders[random.randint(0,2)]}',
            )

        teachers = UserAccount.objects.filter(role=UserRole.TEACHER.value)
        students = UserAccount.objects.filter(role=UserRole.STUDENT.value)
        lesson_types = list(LessonType)
        Lesson_durations = list(LessonDuration)
        lesson_status = list(LessonStatus)
        # increases chances to get booked lessons
        lesson_status.remove(LessonStatus.SAVED)
        lesson_status.append(LessonStatus.FULLFILLED)
        lesson_status.append(LessonStatus.FULLFILLED)

        for i in range(len(students)):
            for _ in range(random.randint(0,6)):
                self.lesson = Lesson.objects.create(
                    type = lesson_types[random.randint(0,len(lesson_types)-1)] ,
                    duration = Lesson_durations[random.randint(0,len(Lesson_durations)-1)] ,
                    lesson_date_time = self.faker.date_time_this_year(tzinfo = timezone.utc).replace(microsecond=0, second=0, minute=0),
                    teacher_id = teachers[random.randint(0,len(teachers)-1)],
                    student_id = students[i],
                    request_date = datetime.date(2022, 10, 15),
                    lesson_status = lesson_status[random.randint(0,len(lesson_status)-1)],
                )


        # seed the invoices base on existing user and bookings
        for i in range(len(students)):   
            student_Id = students[i].id
            students_id_string = str(student_Id)
            
            lessons_with_30 = Lesson.objects.filter(student_id = students[i], lesson_status = LessonStatus.FULLFILLED, duration = LessonDuration.THIRTY)
            lessons_with_45 = Lesson.objects.filter(student_id = students[i], lesson_status = LessonStatus.FULLFILLED, duration = LessonDuration.FOURTY_FIVE)
            lessons_with_1_hr = Lesson.objects.filter(student_id = students[i], lesson_status = LessonStatus.FULLFILLED, duration = LessonDuration.HOUR)
            student_number_of_invoice = Invoice.objects.filter(student_ID = student_Id)


            fees = Invoice.calculate_fees_amount(lessons_with_30, lessons_with_45, lessons_with_1_hr)
            fees = int(fees) # this change the fees type to int so the if loops below will work 

            #this generate random number of pre-exist invoices
            for x in range(random.randint(1,5)):
                pre_fees = random.randint(12, 78)
                number_for_unpaid_and_partially_paid_invoice = random.randint(0, 12)
                pre_reference_number_temp = Invoice.generate_new_invoice_reference_number(students_id_string, x)
                if(number_for_unpaid_and_partially_paid_invoice == 3 or number_for_unpaid_and_partially_paid_invoice == 4):
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.UNPAID, amounts_need_to_pay = pre_fees)
                elif(number_for_unpaid_and_partially_paid_invoice == 5 or number_for_unpaid_and_partially_paid_invoice == 6):
                    amount_paid = random.randint(10, pre_fees)
                    amount_needs_to_be_pay = pre_fees - amount_paid
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.PARTIALLY_PAID, amounts_need_to_pay = amount_needs_to_be_pay)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, transaction_type = TransactionTypes.IN, transaction_amount = amount_paid)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, transaction_type = TransactionTypes.OUT, invoice_reference_transaction = pre_reference_number_temp, transaction_amount = amount_paid)
                else:
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.PAID, amounts_need_to_pay = 0)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, transaction_type = TransactionTypes.IN, transaction_amount = pre_fees)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, transaction_type = TransactionTypes.OUT, invoice_reference_transaction = pre_reference_number_temp, transaction_amount = pre_fees)

            balance_in_student_account = random.randint(1, 200)
            students[i].balance += balance_in_student_account
            students[i].save()
            Transaction.objects.create(Student_ID_transaction = students_id_string, transaction_type = TransactionTypes.IN, transaction_amount = balance_in_student_account)

            reference_number_temp = Invoice.generate_new_invoice_reference_number(students_id_string, len(student_number_of_invoice))

            if(fees != 0):
                Invoice.objects.create(reference_number =  reference_number_temp, student_ID = students_id_string, fees_amount = fees, invoice_status = InvoiceStatus.UNPAID, amounts_need_to_pay = fees)

            #TO DO : add paid, overpaid, and unpaid requests

        # Seed the admins
        for i in range(3):
            fname = self.faker.unique.first_name()
            lname = self.faker.unique.last_name()
            mails = ["gmail.com","yahoo.com","outlook.com","example.org"]
            random_password = ''.join(random.choice(letters) for i in range(10))
            genders = ['M','F','PNOT']

            self.student = UserAccount.objects.create_admin(
                first_name=fname,
                last_name=lname,
                email= f'{fname[0].lower()}{lname.lower()}{random.randint(0,100)}@{mails[random.randint(0,3)]}',
                password=f'{random_password}',
                gender = f'{genders[random.randint(0,2)]}',
            )

        # Seed the director
        for i in range(1):
            fname = self.faker.unique.first_name()
            lname = self.faker.unique.last_name()
            mails = ["gmail.com","yahoo.com","outlook.com","example.org"]
            random_password = ''.join(random.choice(letters) for i in range(10))
            genders = ['M','F','PNOT']

            self.student = UserAccount.objects.create_superuser(
                first_name=fname,
                last_name=lname,
                email= f'{fname[0].lower()}{lname.lower()}{random.randint(0,100)}@{mails[random.randint(0,3)]}',
                password=f'{random_password}',
                gender = f'{genders[random.randint(0,2)]}',
            )

        # CREATE LESSONS
