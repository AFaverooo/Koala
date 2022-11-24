from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from lessons.forms import RequestForm
from lessons.models import Lesson, UserAccount,Gender,UserRole,LessonType,LessonDuration,LessonStatus

from lessons.forms import RequestForm

from django.utils import timezone
from datetime import time
import datetime

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


    def create_saved_lessons(self):
        self.lesson = Lesson.objects.create(
            type = LessonType.INSTRUMENT,
            duration = LessonDuration.THIRTY,
            lesson_date_time = datetime.datetime(2022, 11, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.SAVED
        )



        self.lesson2 = Lesson.objects.create(
            type = LessonType.THEORY,
            duration = LessonDuration.FOURTY_FIVE,
            lesson_date_time = datetime.datetime(2022, 10, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.SAVED
        )

        self.lesson3 = Lesson.objects.create(
            type = LessonType.PERFORMANCE,
            duration = LessonDuration.HOUR,
            lesson_date_time = datetime.datetime(2022, 9, 20, 20, 8, 7, 127325, tzinfo=timezone.utc),
            teacher_id = self.teacher,
            student_id = self.student,
            request_date = datetime.date(2022, 10, 15),
            is_booked = LessonStatus.SAVED
        )

    #first tests cover making a new lesson
    def check_user_information(self,email,name,last_name,gender):
        user = UserAccount.objects.get(email =email)
        self.assertEqual(user.first_name, name)
        self.assertEqual(user.last_name, last_name)
        self.assertEqual(user.gender, gender)
        self.assertEqual(user.email, email)
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)

    def test_sign_up_url(self):
        self.assertEqual(self.url,'/new_lesson/')

    def test_valid_new_lesson_form(self):
        self.assertEqual(len(UserAccount.objects.filter(role = UserRole.TEACHER)), 1)
        form = RequestForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_get_lesson(self):
        self.client.login(email=self.student.email, password="Password123")
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'requests_page.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, RequestForm))
        self.assertFalse(form.is_bound)

    def test_unsuccesful_lesson_request_not_logged_in(self):
        before_count = Lesson.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
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
        response_url = reverse('requests_page')
        #self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'requests_page.html')

        self.check_user_information(self.student.email,self.student.first_name, self.student.last_name, Gender.MALE.value)
        self.check_user_information(self.teacher.email,self.teacher.first_name, self.teacher.last_name, Gender.FEMALE.value)


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
        all_student_pending_lessons = Lesson.objects.filter(is_booked = LessonStatus.PENDING, student_id = self.student)

        self.assertEqual(len(all_student_lessons),len(all_student_pending_lessons))

        for lessons in all_student_lessons:
            self.assertEqual(lessons.is_booked, LessonStatus.PENDING)
            self.assertEqual(lessons.student_id, self.student)

        response_url = reverse('student_feed')

        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'student_feed.html')
