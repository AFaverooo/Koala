

from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus
from lessons.views import make_lesson_timetable_dictionary
import datetime
from django.utils import timezone

class LogInTestCase(TestCase):
    """Tests for the student feed."""

    def setUp(self):
        self.url = reverse('student_feed')

        self.teacher = UserAccount.objects.create_teacher(
            first_name='Barbare',
            last_name='Dutch',
            email='barbdutch@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.teacher2 = UserAccount.objects.create_teacher(
            first_name='Amane',
            last_name='Hill',
            email='amanehill@example.org',
            password='Password123',
            gender = Gender.MALE,
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
            lesson_date_time = datetime.datetime(2022, 11, 20, 15, 15, 00, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.BOOKED
        )

        self.lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 16, 00, 00, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.BOOKED,
        )

        self.lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 9, 45, 00, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.BOOKED,
        )

        self.lesson4 = Lesson.objects.create(
            type = LessonType.PRACTICE,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 12, 25, 9, 45, 00, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.BOOKED,
        )

    def check_dictionary_equality(self, dictionary, type_string, lesson_date_without_time_string, lesson_duration_string, teacher_name):
        self.assertEqual(dictionary['Lesson'] , type_string)
        self.assertEqual(dictionary['Lesson Date'] , lesson_date_without_time_string)
        self.assertEqual(dictionary['Lesson Duration'] , lesson_duration_string)
        self.assertEqual(dictionary['Teacher'] , teacher_name)

    def test_dictionary_format_for_booked_lessons(self):
        lesson_dict = make_lesson_timetable_dictionary(self.student)

        #print(lesson_dict)
        self.assertEqual(len(lesson_dict),4)
        #print(lesson_dict[self.lesson])
        self.check_dictionary_equality(lesson_dict[self.lesson], LessonType.INSTRUMENT.label, "2022-11-20", "15:15 - 15:45", "Miss Barbare Dutch")
        self.check_dictionary_equality(lesson_dict[self.lesson2], LessonType.THEORY.label, "2022-10-20", "16:00 - 16:45", "Miss Barbare Dutch")
        self.check_dictionary_equality(lesson_dict[self.lesson3], LessonType.PERFORMANCE.label, "2022-09-20", "09:45 - 10:45", "Mr Amane Hill")
        self.check_dictionary_equality(lesson_dict[self.lesson4], LessonType.PRACTICE.label, "2022-12-25", "09:45 - 10:30", "Mr Amane Hill")

    def test_get_student_feed_in(self):
        self.client.login(email=self.student.email, password="Password123")
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_feed.html')
