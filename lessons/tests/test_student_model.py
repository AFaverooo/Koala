"""Unit tests for the Student model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Student,is_valid_gender, is_valid_role

class StudentModelTestCase(TestCase):
    """Unit tests for the Student model"""

    def setUp(self):
        self.student = Student.objects.create_user(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = 'M',
            role = 'Student'
        )

    def _create_second_student(self):
        student = Student.objects.create_user(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            gender = 'F',
            role = 'Student'
        )
        return student

    def _create_third_student(self):
        student = Student.objects.create_user(
            first_name='Michael',
            last_name='Phoenix',
            email='mikephoenix@example.org',
            password='Password123',
            gender = 'PNOT',
            role = 'Student'
        )
        return student

    def _assert_student_is_valid(self):
        try:
            self.student.full_clean()
        except(ValidationError):
            self.fail('Test user should be valid')

    def _assert_student_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.student.full_clean()


    #tests for students name
    def test_first_name_must_not_be_blank(self):
        self.student.first_name = ''
        self._assert_student_is_invalid()

    def test_first_name_need_not_be_unique(self):
        second_student = self._create_second_student()
        self.student.first_name = second_student.first_name
        self._assert_student_is_valid()

    def test_first_name_may_contain_50_characters(self):
        self.student.first_name = 'x' * 50
        self._assert_student_is_valid()

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.student.first_name = 'x' * 51
        self._assert_student_is_invalid()

    #tests for student last name
    def test_last_name_must_not_be_blank(self):
        self.student.last_name = ''
        self._assert_student_is_invalid()

    def test_last_name_need_not_be_unique(self):
        second_student = self._create_second_student()
        self.student.last_name = second_student.last_name
        self._assert_student_is_valid()

    def test_last_name_may_contain_50_characters(self):
        self.student.last_name = 'x' * 50
        self._assert_student_is_valid()

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.student.last_name = 'x' * 51
        self._assert_student_is_invalid()

    #tests for student email
    def test_email_must_not_be_blank(self):
        self.student.email = ''
        self._assert_student_is_invalid()

    def test_email_must_be_unique(self):
        second_student = self._create_second_student()
        self.student.email = second_student.email
        self._assert_student_is_invalid()

    def test_email_must_contain_at_symbol(self):
        self.student.email = 'johndoe.example.org'
        self._assert_student_is_invalid()

    def test_email_must_contain_domain_name(self):
        self.student.email = 'johndoe@.org'
        self._assert_student_is_invalid()

    def test_email_must_contain_domain(self):
        self.student.email = 'johndoe@example'
        self._assert_student_is_invalid()

    def test_email_must_not_contain_more_than_one_at(self):
        self.student.email = 'johndoe@@example.org'
        self._assert_student_is_invalid()

    def test_student_selected_gender_is_valid(self):
        self._assert_student_is_valid()

    #checks students of gender M,F,PNOT are valid
    def test_student_gender_string_is_valid(self):
        self.assertTrue(is_valid_gender(self.student))
        self.assertTrue(is_valid_gender(self._create_second_student()))
        self.assertTrue(is_valid_gender(self._create_third_student()))

    def test_student_gender_string_is_invalid(self):
        self.student.gender = 'MALE'
        self.assertFalse(is_valid_gender(self.student))

    def test_student_role_is_valid(self):
        self.assertTrue(is_valid_role(self.student))
        self.assertTrue(is_valid_role(self._create_second_student()))
        self.assertTrue(is_valid_role(self._create_third_student()))

    def test_student_role_string_is_invalid(self):
        self.student.role = 'NonStudent'
        self.assertFalse(is_valid_role(self.student))
