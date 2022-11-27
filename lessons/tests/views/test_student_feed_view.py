

from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus
from lessons.views import make_lesson_timetable_dictionary,make_unfulfilled_dictionary
import datetime
from django.utils import timezone

class StudentFeedTestCase(TestCase):
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

        self.teacher3 = UserAccount.objects.create_teacher(
            first_name='Jonathan',
            last_name='Jacks',
            email='johnjacks@example.org',
            password='Password123',
            gender = Gender.PNOT,
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
            lesson_date_time = datetime.datetime(2022, 11, 20, 15, 15, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED
        )

        self.lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 16, 00, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson4 = Lesson.objects.create(
            type = LessonType.PRACTICE,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 12, 25, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher2,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

        self.lesson5 = Lesson.objects.create(
            type = LessonType.PRACTICE,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 9, 25, 9, 45, 00, tzinfo=timezone.utc),
            teacher_id = self.teacher3,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.FULLFILLED,
        )

    def change_lessons_status_to_unfulfilled(self):
        self.lesson.lesson_status = LessonStatus.UNFULFILLED
        self.lesson.save()
        self.lesson2.lesson_status = LessonStatus.UNFULFILLED
        self.lesson2.save()
        self.lesson3.lesson_status = LessonStatus.UNFULFILLED
        self.lesson3.save()
        self.lesson4.lesson_status = LessonStatus.UNFULFILLED
        self.lesson4.save()
        self.lesson5.lesson_status = LessonStatus.UNFULFILLED
        self.lesson5.save()

    def check_unfulfilled_dictionary_equality(self,dictionary, request_number, lesson_date_without_time_string, type_string, lesson_duration_string, teacher_name):
        self.assertEqual(dictionary['Lesson Request'] , request_number)
        self.assertEqual(dictionary['Lesson Date'] , lesson_date_without_time_string)
        self.assertEqual(dictionary['Lesson'] , type_string)
        self.assertEqual(dictionary['Lesson Duration'] , lesson_duration_string)
        self.assertEqual(dictionary['Teacher'] , teacher_name)

    def check_fulfilled_dictionary_equality(self, dictionary, type_string, lesson_date_without_time_string, lesson_duration_string, teacher_name):
        self.assertEqual(dictionary['Lesson'] , type_string)
        self.assertEqual(dictionary['Lesson Date'] , lesson_date_without_time_string)
        self.assertEqual(dictionary['Lesson Duration'] , lesson_duration_string)
        self.assertEqual(dictionary['Teacher'] , teacher_name)

    def test_dictionary_format_for_unfulfilled_lessons(self):
        self.change_lessons_status_to_unfulfilled()

        unfulfilled_lessons_dict = make_unfulfilled_dictionary(self.student)

        self.assertEqual(len(unfulfilled_lessons_dict),5)
        #print(lesson_dict[self.lesson])
        self.check_unfulfilled_dictionary_equality(unfulfilled_lessons_dict[self.lesson],'0',"2022-11-20", "INSTRUMENT", "30 minutes", "Barbare Dutch")
        self.check_unfulfilled_dictionary_equality(unfulfilled_lessons_dict[self.lesson2],'1',"2022-10-20", "THEORY", "45 minutes", "Barbare Dutch")
        self.check_unfulfilled_dictionary_equality(unfulfilled_lessons_dict[self.lesson3],'2',"2022-09-20", "PERFORMANCE", "60 minutes", "Amane Hill")
        self.check_unfulfilled_dictionary_equality(unfulfilled_lessons_dict[self.lesson4],'3',"2022-12-25", "PRACTICE", "45 minutes", "Amane Hill")
        self.check_unfulfilled_dictionary_equality(unfulfilled_lessons_dict[self.lesson5],'4',"2022-09-25", "PRACTICE", "45 minutes", "Jonathan Jacks")

    def test_dictionary_format_for_fullfilled_lessons(self):
        lesson_dict = make_lesson_timetable_dictionary(self.student)

        #print(lesson_dict)
        self.assertEqual(len(lesson_dict),5)
        #print(lesson_dict[self.lesson])
        self.check_fulfilled_dictionary_equality(lesson_dict[self.lesson], LessonType.INSTRUMENT.label, "2022-11-20", "15:15 - 15:45", "Miss Barbare Dutch")
        self.check_fulfilled_dictionary_equality(lesson_dict[self.lesson2], LessonType.THEORY.label, "2022-10-20", "16:00 - 16:45", "Miss Barbare Dutch")
        self.check_fulfilled_dictionary_equality(lesson_dict[self.lesson3], LessonType.PERFORMANCE.label, "2022-09-20", "09:45 - 10:45", "Mr Amane Hill")
        self.check_fulfilled_dictionary_equality(lesson_dict[self.lesson4], LessonType.PRACTICE.label, "2022-12-25", "09:45 - 10:30", "Mr Amane Hill")
        self.check_fulfilled_dictionary_equality(lesson_dict[self.lesson5], LessonType.PRACTICE.label, "2022-09-25", "09:45 - 10:30", "Jonathan Jacks")

    def test_get_student_feed(self):
        self.client.login(email=self.student.email, password="Password123")

        response = self.client.get(self.url)
        fullfilled_lessons = response.context['fullfilled_lessons']
        greeting_str = response.context['greeting']

        self.assertEqual(len(fullfilled_lessons),5)
        self.assertEqual(greeting_str, "Welcome back John Doe Below is your timetable for this term")
        self.assertEqual(len(fullfilled_lessons),5)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_feed.html')

    def test_get_student_feed_with_pending_lessons(self):
        self.change_lessons_status_to_unfulfilled()
        self.client.login(email=self.student.email, password="Password123")

        response = self.client.get(self.url)
        fullfilled_lessons = response.context['unfulfilled_requests']
        greeting_str = response.context['greeting']

        self.assertEqual(len(fullfilled_lessons),5)
        self.assertEqual(greeting_str, "Welcome back John Doe Below are your lesson requests")
        self.assertEqual(len(fullfilled_lessons),5)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'student_feed.html')
