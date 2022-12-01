from django.test import TestCase
from django.urls import reverse
from lessons.models import UserAccount, Lesson, UserRole, Gender, LessonType,LessonDuration,LessonStatus
from lessons.views import make_lesson_timetable_dictionary,make_lesson_dictionary
import datetime
from django.utils import timezone
from django.contrib import messages
# from lessons.models import UserAccount, Gender
from lessons.tests.helpers import reverse_with_next

class StudentFeedDeleteLessonTestCase(TestCase):
    """Tests for the student feed."""

    def setUp(self):

        self.admin = UserAccount.objects.create_admin(
            first_name='Bob',
            last_name='Jacobs',
            email='bobby@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

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

        self.delete_url = reverse('delete_pending', kwargs={'lesson_id':self.lesson.lesson_id})


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


    def test_delete_pending_url(self):
        self.assertEqual(self.delete_url, f'/delete_pending/{self.lesson.lesson_id}')

    def test_get_delete_pending_lessons_url(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.delete_url, follow = True)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')

    def test_attempt_deletion_of_other_student_lessons(self):
        self.student_jane = UserAccount.objects.create_student(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )

        self.client.login(email=self.student_jane.email, password="Password123")
        before_count = Lesson.objects.count()
        response = self.client.post(self.delete_url, follow = True)
        after_count = Lesson.objects.count()

        self.assertEqual(before_count,after_count)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Attempted Deletion Not Permitted')
        self.assertEqual(messages_list[0].level, messages.WARNING)

        self.assertTemplateUsed(response, 'student_feed.html')

    def test_student_not_logged_in_deleting_lessons(self):
        response = self.client.get(self.delete_url, follow = True)
        redirect_url = reverse('home')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'home.html')

    #prev causing errors
    def test_not_student_accessing_deleting_pending_lessons(self):
        self.client.login(email=self.admin.email, password="Password123")
        response = self.client.get(self.delete_url, follow = True)
        redirect_url = reverse('admin_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'admin_feed.html')

    def test_incorrect_deletion_of_lesson(self):
        self.client.login(email=self.student.email, password="Password123")
        before_count = Lesson.objects.count()
        self.delete_url = reverse('delete_pending', kwargs={'lesson_id':60})
        response = self.client.post(self.delete_url, follow = True)
        after_count = Lesson.objects.count()
        self.assertEqual(before_count, after_count)

        self.assertEqual(Lesson.objects.filter(student_id = self.student).count(),5)

        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Attempted Deletion Not Permitted')
        self.assertEqual(messages_list[0].level, messages.WARNING)

        self.assertTemplateUsed(response, 'student_feed.html')

    def test_succesful_deletion_of_lesson(self):
        self.change_lessons_status_to_unfulfilled()

        self.client.login(email=self.student.email, password="Password123")
        before_count = Lesson.objects.count()
        response = self.client.post(self.delete_url, follow = True)
        after_count = Lesson.objects.count()
        self.assertEqual(before_count-1, after_count)
        self.assertEqual(Lesson.objects.filter(student_id = self.student).count(),4)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')

        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Lesson request deleted')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

    def test_succesful_multiple_deletion_of_lesson(self):
        self.change_lessons_status_to_unfulfilled()
        before_count = Lesson.objects.count()

        self.client.login(email=self.student.email, password="Password123")

        response = self.client.post(self.delete_url, follow = True)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')
        messages_list = list(response.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Lesson request deleted')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        self.delete_url = reverse('delete_pending', kwargs={'lesson_id':self.lesson2.lesson_id})
        response_second = self.client.post(self.delete_url, follow = True)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response_second, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response_second, 'student_feed.html')
        messages_list = list(response_second.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Lesson request deleted')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        self.delete_url = reverse('delete_pending', kwargs={'lesson_id':self.lesson3.lesson_id})
        response_third = self.client.post(self.delete_url, follow = True)
        redirect_url = reverse('student_feed')
        self.assertRedirects(response_third, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response_third, 'student_feed.html')

        messages_list = list(response_third.context['messages'])
        self.assertEqual(str(messages_list[0]), 'Lesson request deleted')
        self.assertEqual(messages_list[0].level, messages.SUCCESS)

        after_count = Lesson.objects.count()
        self.assertEqual(before_count-3, after_count)
        self.assertEqual(Lesson.objects.filter(student_id = self.student).count(),2)
        #self.assertTemplateUsed(response, 'student_feed.html')
