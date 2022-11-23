from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount,Lesson,Gender,LessonType,LessonDuration,LessonStatus

from django.utils import timezone
from datetime import time
import datetime

class StudentViewTestCase(TestCase):
    """Tests for the admin feed."""

    def setUp(self):
        self.url = reverse('admin_feed')

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = 'M',
        )
        self.teacher = UserAccount.objects.create_teacher(
            first_name='Barbare',
            last_name='Dutch',
            email='barbdutch@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.pending_lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.PENDING
        )

        self.booked_lesson = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.BOOKED
        )


    def test_get_admin_feed_in(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_feed.html')


    # TODO: admin can see pending or booked requests (after requests form is complete)
