from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration, is_valid_lessonDuration,is_valid_lessonType

from django.utils import timezone

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

        self.lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = '2006-10-25 14:30:59',
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = '2022-10-25',
        )


    def _assert_lesson_is_valid(self):
        try:
            self.lesson.full_clean()
        except(ValidationError):
            self.fail('Test user should be valid')

    def _assert_lesson_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.lesson.full_clean()


    def test_lesson_is_valid(self):
        self._assert_lesson_is_valid()

    def test_lesson_type_is_valid(self):
        self.assertTrue(is_valid_lessonType(self.lesson))

    def test_lesson_duration_is_valid(self):
        self.assertTrue(is_valid_lessonDuration(self.lesson))

    def test_lesson_type_is_invalid(self):
        self.lesson.type = 'NONlessonType'
        self.assertFalse(is_valid_lessonType(self.lesson))
        self._assert_lesson_is_invalid()

    def test_lesson_duration_is_invalid(self):
        self.lesson.duration = 'randomDuration'
        self.assertFalse(is_valid_lessonDuration(self.lesson))
        self._assert_lesson_is_invalid()
