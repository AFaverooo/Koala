from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import UserAccount, UserRole, Gender
import random
import string

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

        # Seed the remaining students,teachers,admins and directors into the database
        for i in range(20):

            fname = self.faker.first_name()
            lname = self.faker.last_name()
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

        for i in range(5):

            fname = self.faker.first_name()
            lname = self.faker.last_name()
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


        for i in range(3):
            fname = self.faker.first_name()
            lname = self.faker.last_name()
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

        for i in range(1):
            fname = self.faker.first_name()
            lname = self.faker.last_name()
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
