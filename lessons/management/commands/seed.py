from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus,Invoice, InvoiceStatus, Transaction
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
        seed_lesson_id = 100000 #seed lesson id number is big, in case to be same as existing lesson id
        for i in range(len(students)):   
            student_Id = students[i].id
            students_id_string = str(student_Id)

            #this generate random number of pre-exist invoices and payments
            for x in range(random.randint(1,5)):
                pre_fees = random.randint(12, 78)
                probability = random.randint(0, 12)
                pre_reference_number_temp = Invoice.generate_new_invoice_reference_number(students_id_string, x)
                if(probability == 3 or probability == 4):
                    # unpaid invoice
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.UNPAID, amounts_need_to_pay = pre_fees, lesson_ID = seed_lesson_id)
                elif(probability == 5 or probability == 6):
                    # partially paid invoice
                    amount_paid = random.randint(10, pre_fees)
                    amount_needs_to_be_pay = pre_fees - amount_paid
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.PARTIALLY_PAID, amounts_need_to_pay = amount_needs_to_be_pay,lesson_ID = seed_lesson_id)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, invoice_reference_transaction = pre_reference_number_temp, transaction_amount = amount_paid)
                elif(probability == 7):
                    # overpaid invoice
                    amount_paid = random.randint(pre_fees+100, pre_fees + 200)
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.PARTIALLY_PAID, amounts_need_to_pay = 0, lesson_ID = seed_lesson_id)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, invoice_reference_transaction = pre_reference_number_temp, transaction_amount = amount_paid)
                else:
                    Invoice.objects.create(reference_number =  pre_reference_number_temp, student_ID = students_id_string, fees_amount = pre_fees, invoice_status = InvoiceStatus.PAID, amounts_need_to_pay = 0, lesson_ID = seed_lesson_id)
                    Transaction.objects.create(Student_ID_transaction = students_id_string, invoice_reference_transaction = pre_reference_number_temp, transaction_amount = pre_fees)
                seed_lesson_id+=1

            # create a new invoice for each existing lesson
            lessons_booked = Lesson.objects.filter(student_id = students[i], lesson_status = LessonStatus.FULLFILLED)
            for lesson in lessons_booked:
                fees = Invoice.calculate_fees_amount(lesson.duration)
                student_number_of_invoice_pre_exist = Invoice.objects.filter(student_ID = student_Id)
                reference_number_temp = Invoice.generate_new_invoice_reference_number(students_id_string, len(student_number_of_invoice_pre_exist))
                Invoice.objects.create(reference_number =  reference_number_temp, student_ID = students_id_string, fees_amount = fees, invoice_status = InvoiceStatus.UNPAID, amounts_need_to_pay = fees, lesson_ID = lesson.lesson_id)


            # this calculate the balance for student
            current_existing_invoice = Invoice.objects.filter(student_ID = student_Id)
            current_existing_transaction = Transaction.objects.filter(Student_ID_transaction = student_Id)
            invoice_fee_total = 0
            payment_fee_total = 0

            for invoice in current_existing_invoice:
                invoice_fee_total += invoice.fees_amount

            for transaction in current_existing_transaction:
                payment_fee_total += transaction.transaction_amount

            students[i].balance = payment_fee_total - invoice_fee_total
            students[i].save()

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
