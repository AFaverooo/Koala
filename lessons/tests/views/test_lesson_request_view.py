from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole,LessonType,LessonDuration,LessonStatus

from lessons.forms import RequestForm
from lessons.views import get_saved_lessons,get_unfulfilled_lessons

from django.utils import timezone
from datetime import time
import datetime

from django.db import IntegrityError
from django.db import transaction

class LessonRequestViewTestCase(TestCase):
    def setUp(self):

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
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

        self.url = reverse('new_lesson')

        self.save_lessons_url = reverse('save_lessons')

        self.form_input = {
            'type': LessonType.INSTRUMENT,
            'duration': LessonDuration.THIRTY,
            'lesson_date_time_0': datetime.date(2022, 4, 4),
            'lesson_date_time_1': time(15, 15, 15),

            'teachers': UserAccount.objects.filter(role = UserRole.TEACHER).first().id,
        }

    def create_lesson_form_copy(self):
        self.form_input_copy = {
            'type': LessonType.INSTRUMENT,
            'duration': LessonDuration.THIRTY,
            'lesson_date_time_0': datetime.date(2022, 4, 4),
            'lesson_date_time_1': time(15, 15, 15),

            'teachers': UserAccount.objects.filter(role = UserRole.TEACHER).first().id,
        }

    def create_saved_lessons(self):
        self.saved_lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )



        self.saved_lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )

        self.saved_lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.SAVED
        )

    def create_unfulfilled_lessons(self):
        self.unfulfilled_lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2021, 11, 20, 20, 8, 7,tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.UNFULFILLED
        )

        self.unfulfilled_lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2021, 10, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.UNFULFILLED
        )
        self.unfulfilled_lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2021, 9, 20, 20, 8, 7, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            lesson_status = LessonStatus.UNFULFILLED
        )

    def delete_saved_lessons(self):
        self.saved_lesson.delete()
        self.saved_lesson2.delete()
        self.saved_lesson3.delete()

    def delete_unfulfilled_lessons(self):
        self.unfulfilled_lesson.delete()
        self.unfulfilled_lesson2.delete()
        self.unfulfilled_lesson3.delete()

    #FIRST TESTS COVER FUNCTIONALITY TO ADD A NEW LESSON IN SAVED STATE

    def check_user_information(self,email,name,last_name,gender):
        user = UserAccount.objects.get(email =email)
        self.assertEqual(user.first_name, name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.gender, gender)
        self.assertEqual(user.email, email)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    def test_get_saved_lessons(self):
        self.create_saved_lessons()

        saved_lessons = get_saved_lessons(self.student)

        self.assertEqual(len(saved_lessons),3)

    def test_get_unfulfilled_lessons(self):
        self.create_unfulfilled_lessons()

        unfulfilled_lessons = get_unfulfilled_lessons(self.student)

        self.assertEqual(len(unfulfilled_lessons),3)

    def test_request_url(self):
        self.assertEqual(self.url,'/new_lesson/')

    def test_valid_new_lesson_form(self):
        self.assertEqual(len(UserAccount.objects.filter(role = UserRole.TEACHER)), 1)
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_get_requests_page_without_lessons_saved(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']

        self.assertEqual(len(response.context['lessons']),0)

        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)


    def test_get_requests_page_with_lessons_saved(self):
        self.create_saved_lessons()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']

        self.assertEqual(len(response.context['lessons']),3)

        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

        self.delete_saved_lessons()

    def test_unsuccesful_lesson_request_not_logged_in(self):
        before_count = Lesson.objects.count()
        response = self.client.get(self.url, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count)

        response_url = reverse('log_in')
        self.assertTemplateUsed(response, 'log_in.html')


    def test_unsuccesful_lesson_request_bad_data(self):
        self.client.login(email=self.student.email, password="Password123")
        self.form_input['type'] = 'BAD CHOICE'

        before_count = UserAccount.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = UserAccount.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RequestForm))
        self.assertTrue(form.is_bound)

    def test_succesful_request(self):
        self.client.login(email=self.student.email, password="Password123")

        before_count = Lesson.objects.count()

        response = self.client.post(self.url, self.form_input, follow=True)

        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count+1)
        #self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')

        self.check_user_information(self.student.email,self.student.first_name, self.student.last_name, Gender.MALE.value)
        self.check_user_information(self.teacher.email,self.teacher.first_name, self.teacher.last_name, Gender.FEMALE.value)


    def test_make_lesson_form_copy(self):

        self.client.login(email=self.student.email, password="Password123")
        before_count = Lesson.objects.count()

        response = self.client.post(self.url, self.form_input, follow=True)

        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count+1)

        self.assertTemplateUsed(response, 'requests_page.html')

        self.create_lesson_form_copy()
        before_copy_count = Lesson.objects.count()
        response_copy = self.client.post(self.url, self.form_input_copy, follow=True)
        after_copy_count = Lesson.objects.count()
        self.assertEqual(before_copy_count,after_copy_count)
        self.assertTemplateUsed(response, 'requests_page.html')

    def test_save_lessons_url(self):
        self.assertEqual(self.save_lessons_url,'/save_lessons/')

    def test_save_lessons_not_logged_in(self):
        before_count = Lesson.objects.count()
        response = self.client.get(self.save_lessons_url, follow=True)
        after_count = Lesson.objects.count()
        self.assertEqual(after_count, before_count)
        response_url = reverse('log_in')
        self.assertTemplateUsed(response, 'log_in.html')

    def test_save_lessons_get(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.save_lessons_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertEqual(len(response.context['lessons']),0)

        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

    def test_save_lessons_get_with_lessons(self):
        self.create_saved_lessons()
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.save_lessons_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']

        self.assertEqual(len(response.context['lessons']),3)

        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

        self.delete_saved_lessons()



    def test_succesfull_save_lessons_post(self):
        self.create_saved_lessons()
        #test normally fails after login required is added
        self.client.login(email = self.student.email, password = 'Password123')
        before_count = Lesson.objects.count()
        response = self.client.post(self.save_lessons_url, follow = True)
        after_count = Lesson.objects.count()

        self.assertEqual(before_count,after_count)

        self.assertEqual(response.status_code, 200)

        all_student_lessons = Lesson.objects.filter(student_id = self.student)
        all_student_unfulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED, student_id = self.student)

        self.assertEqual(len(all_student_lessons),len(all_student_unfulfilled_lessons))

        for lessons in all_student_lessons:
            self.assertEqual(lessons.lesson_status, LessonStatus.UNFULFILLED)
            self.assertEqual(lessons.student_id, self.student)

        self.assertTemplateUsed(response, 'requests_page.html')
