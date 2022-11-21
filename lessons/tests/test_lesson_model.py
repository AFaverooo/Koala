from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration


class LessonModelTestCase(TestCase):

    def setUp(self):

        self.teacher = UserAccount.objects.create_teacher(
            first_name='Barbare',
            last_name='Dutch',
            email='barbdutch@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = Gender.MALE,
        )
