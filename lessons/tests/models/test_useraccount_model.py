"""Unit tests for the UserAccount model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import UserAccount,UserRole, Gender

from lessons.modelHelpers import is_valid_gender,is_valid_role

class UserAccountModelTestCase(TestCase):
    """Unit tests for the UserAccount model"""

    #fixtures = ['lessons/tests/fixtures/john-fixtures.json']

    def setUp(self):
        #self.student=UserAccount.objects.get(email='johndoe@example.org')
        #self.student.role = UserRole.STUDENT
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

        self.admin = UserAccount.objects.create_admin(
            first_name='Bob',
            last_name='Jacobs',
            email='bobby@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

    def _create_second_student(self):
        student = UserAccount.objects.create_student(
            first_name='Jane',
            last_name='Doe',
            email='janedoe@example.org',
            password='Password123',
            gender = Gender.FEMALE,
        )
        return student

    def _create_third_student(self):
        student = UserAccount.objects.create_student(
            first_name='Michael',
            last_name='Phoenix',
            email='mikephoenix@example.org',
            password='Password123',
            gender = Gender.PNOT,
        )
        return student

    def _assert_useraccount_is_valid(self,account):
        try:
            account.full_clean()
        except(ValidationError):
            self.fail('Test user should be valid')

    def _assert_useraccount_is_invalid(self,account):
        with self.assertRaises(ValidationError):
            account.full_clean()

    #tests for students name
    def test_first_name_must_not_be_blank(self):
        self.student.first_name = ''
        self._assert_useraccount_is_invalid(self.student)

    def test_first_name_need_not_be_unique(self):
        second_student = self._create_second_student()
        self.student.first_name = second_student.first_name
        self._assert_useraccount_is_valid(self.student)

    def test_first_name_may_contain_50_characters(self):
        self.student.first_name = 'x' * 50
        self._assert_useraccount_is_valid(self.student)

    def test_first_name_must_not_contain_more_than_50_characters(self):
        self.student.first_name = 'x' * 51
        self._assert_useraccount_is_invalid(self.student)

    #tests for student last name
    def test_last_name_must_not_be_blank(self):
        self.student.last_name = ''
        self._assert_useraccount_is_invalid(self.student)

    def test_last_name_need_not_be_unique(self):
        second_student = self._create_second_student()
        self.student.last_name = second_student.last_name
        self._assert_useraccount_is_valid(self.student)

    def test_last_name_may_contain_50_characters(self):
        self.student.last_name = 'x' * 50
        self._assert_useraccount_is_valid(self.student)

    def test_last_name_must_not_contain_more_than_50_characters(self):
        self.student.last_name = 'x' * 51
        self._assert_useraccount_is_invalid(self.student)

    #tests for student email
    def test_email_must_not_be_blank(self):
        self.student.email = ''
        self._assert_useraccount_is_invalid(self.student)

    def test_email_must_be_unique(self):
        second_student = self._create_second_student()
        self.student.email = second_student.email
        self._assert_useraccount_is_invalid(self.student)

    def test_email_must_contain_at_symbol(self):
        self.student.email = 'johndoe.example.org'
        self._assert_useraccount_is_invalid(self.student)

    def test_email_must_contain_domain_name(self):
        self.student.email = 'johndoe@.org'
        self._assert_useraccount_is_invalid(self.student)

    def test_email_must_contain_domain(self):
        self.student.email = 'johndoe@example'
        self._assert_useraccount_is_invalid(self.student)

    def test_email_must_not_contain_more_than_one_at(self):
        self.student.email = 'johndoe@@example.org'
        self._assert_useraccount_is_invalid(self.student)

    def test_student_is_valid(self):
        self._assert_useraccount_is_valid(self.student)

    #checks students of gender M,F,PNOT are valid
    def test_student_gender_string_is_valid(self):
        self.assertTrue(is_valid_gender(self.student))
        self.assertTrue(is_valid_gender(self._create_second_student()))
        self.assertTrue(is_valid_gender(self._create_third_student()))

    def test_student_gender_must_be_invalid(self):
        self.student.gender = 'NOTVALIDGENDER'
        self.assertFalse(is_valid_gender(self.student))
        self._assert_useraccount_is_invalid(self.student)

    def test_student_role_is_valid(self):
        self.assertTrue(is_valid_role(self.student))
        self.assertTrue(is_valid_role(self._create_second_student()))
        self.assertTrue(is_valid_role(self._create_third_student()))

    def test_student_role_string_must_be_valid(self):
        self.student.role = 'NonUserAccount'
        self.assertFalse(is_valid_role(self.student))
        self._assert_useraccount_is_invalid(self.student)

    def test_admin_role_is_valid(self):
        self.assertTrue(is_valid_role(self.admin))
        self._assert_useraccount_is_valid(self.admin)

    def test_teacher_role_is_valid(self):
        self.assertTrue(is_valid_role(self.teacher))
        self._assert_useraccount_is_valid(self.teacher)

    def test_admin_is_staff(self):
        self.assertTrue(self.admin.is_staff)
        self._assert_useraccount_is_valid(self.admin)

    def test_teacher_is_staff(self):
        self.assertTrue(self.teacher.is_staff)
        self._assert_useraccount_is_valid(self.teacher)

    def test_student_is_not_staff(self):
        self.assertFalse(self.student.is_staff)
        self._assert_useraccount_is_valid(self.student)

    def test_student_is_student(self):
        self.assertTrue(self.student.role.is_student())
        self._assert_useraccount_is_valid(self.student)

    def test_student_is_not_student(self):
        self.student.role = UserRole.ADMIN
        self.assertFalse(self.student.role.is_student())

    def test_student_not_parent(self):
        second_student = self._create_second_student()
        third_student = self._create_third_student()

        self.assertFalse(self.student.is_parent)
        self.assertEqual(self.student.parent_of_user,None)
        self.assertFalse(second_student.is_parent)
        self.assertEqual(second_student.parent_of_user,None)
        self.assertFalse(third_student.is_parent)
        self.assertEqual(third_student.parent_of_user,None)

    def test_balance_can_be_blank(self):
        self.student.balance = ''
        self._assert_useraccount_is_valid(self.student)

    def test_balance_default_value_is_0(self):
        self.assertEqual(self.student.balance, 0)

    def test_balance_can_be_larger_than_0(self):
        self.student.balance = 10000
        self._assert_useraccount_is_valid(self.student)

    def test_balance_can_be_0(self):
        self.student.balance = 0
        self._assert_useraccount_is_valid(self.student)

    def test_balance_can_be_smaller_than_0(self):
        self.student.balance = -1
        self._assert_useraccount_is_valid(self.student)

    def test_balance_must_not_be_unique(self):
        second_student = self._create_second_student()
        self.student.balance = second_student.balance
        self._assert_useraccount_is_valid(self.student)

    def test_balance_must_only_contain_number(self):
        self.student.balance = '45s'
        self._assert_useraccount_is_invalid(self.student)
