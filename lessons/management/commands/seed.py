from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus
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
        lesson_status.append(LessonStatus.BOOKED)
        lesson_status.append(LessonStatus.BOOKED)

        for i in range(len(students)):
            for _ in range(random.randint(0,6)):
                self.lesson = Lesson.objects.create(
                    type = lesson_types[random.randint(0,len(lesson_types)-1)] ,
                    duration = Lesson_durations[random.randint(0,len(Lesson_durations)-1)] ,
                    lesson_date_time = self.faker.date_time_this_year(tzinfo = timezone.utc).replace(microsecond=0, second=0, minute=0),
                    teacher_id = teachers[random.randint(0,len(teachers)-1)],
                    student_id = students[i],
                    request_date = datetime.date(2022, 10, 15),
                    is_booked = lesson_status[random.randint(0,len(lesson_status)-1)],
                )

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
