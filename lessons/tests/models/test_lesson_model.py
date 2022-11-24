from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration, is_valid_lessonDuration,is_valid_lessonType

from django.db import IntegrityError

import datetime
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
            lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
        )



        self.lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
        )

        self.lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
        )

    def test_violate_primary_key_unique_constraint(self):
        with self.assertRaises(IntegrityError):
            self.lessonCopy = Lesson.objects.create(
                type = LessonType.INSTRUMENT,
                duration = LessonDuration.THIRTY,
                lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
                teacher_id = self.teacher,
                student_id = self.student,
                request_date = datetime.date(2022, 10, 15),
                )


    def _assert_lesson_is_valid(self,lesson):
        try:
            lesson.full_clean()
        except(ValidationError):
            self.fail('Test user should be valid')

    def _assert_lesson_is_invalid(self,lesson):
        with self.assertRaises(ValidationError):
            lesson.full_clean()

    def _all_lessons_are_valid(self):
        self._assert_lesson_is_valid(self.lesson)
        self._assert_lesson_is_valid(self.lesson2)
        self._assert_lesson_is_valid(self.lesson3)

    def test_all_lessons_are_valid(self):
        self._all_lessons_are_valid()

    def test_lesson_dates_are_different(self):
        self.assertNotEqual(self.lesson.lesson_date_time, self.lesson2.lesson_date_time)
        self.assertNotEqual(self.lesson.lesson_date_time, self.lesson3.lesson_date_time)
        self.assertNotEqual(self.lesson2.lesson_date_time, self.lesson3.lesson_date_time)
        self._all_lessons_are_valid()

    def test_all_lesson_types_are_valid(self):
        self.assertTrue(is_valid_lessonType(self.lesson))
        self.assertTrue(is_valid_lessonType(self.lesson2))
        self.assertTrue(is_valid_lessonType(self.lesson3))

        self._all_lessons_are_valid()

    def test_all_lesson_durations_are_valid(self):
        self.assertTrue(is_valid_lessonDuration(self.lesson))
        self.assertTrue(is_valid_lessonDuration(self.lesson2))
        self.assertTrue(is_valid_lessonDuration(self.lesson3))

        self._all_lessons_are_valid()

    def test_lesson_type_is_invalid(self):
        self.lesson.type = 'NONlessonType'
        self.assertFalse(is_valid_lessonType(self.lesson))
        self._assert_lesson_is_invalid(self.lesson)

    def test_lesson_duration_is_invalid(self):
        self.lesson.duration = 'randomDuration'
        self.assertFalse(is_valid_lessonDuration(self.lesson))
        self._assert_lesson_is_invalid(self.lesson)

    def test_lesson2_type_is_invalid(self):
        self.lesson2.type = 'NONlessonType2'
        self.assertFalse(is_valid_lessonType(self.lesson2))
        self._assert_lesson_is_invalid(self.lesson2)

    def test_lesson2_duration_is_invalid(self):
        self.lesson2.duration = 'randomDuration2'
        self.assertFalse(is_valid_lessonDuration(self.lesson2))
        self._assert_lesson_is_invalid(self.lesson2)

    def test_all_lessons_request_date_is_equal(self):
        self.assertEqual(self.lesson.request_date, self.lesson2.request_date)
        self.assertEqual(self.lesson.request_date, self.lesson3.request_date)
        self.assertEqual(self.lesson2.request_date, self.lesson3.request_date)
