"""Unit tests for the UserAccount model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import UserAccount,Term

from lessons.modelHelpers import is_valid_gender,is_valid_role
import datetime

class UserAccountModelTestCase(TestCase):
    """Unit tests for the UserAccount model"""

    def setUp(self):
        # Term.objects.create(
        #     term_number=1,
        #     start_date = datetime.date(2022, 9,1),
        #     end_date = datetime.date(2022, 10,21),
        # )

        # Term.objects.create(
        #     term_number=2,
        #     start_date = datetime.date(2022, 10,31),
        #     end_date = datetime.date(2022, 12,16),
        # )

        # Term.objects.create(
        #     term_number=3,
        #     start_date = datetime.date(2023, 1,3),
        #     end_date = datetime.date(2023, 2,10),
        # )

        # Term.objects.create(
        #     term_number=4,
        #     start_date = datetime.date(2023, 2,20),
        #     end_date = datetime.date(2023, 3,31),
        # )

        # Term.objects.create(
        #     term_number=5,
        #     start_date = datetime.date(2023, 4,17),
        #     end_date = datetime.date(2023, 5,26),
        # )

        # Term.objects.create(
        #     term_number=6,
        #     start_date = datetime.date(2023, 6,5),
        #     end_date = datetime.date(2023, 7,21),
        # )

        self.term = Term.objects.create(
            term_number=1,
            start_date = datetime.date(2022, 9,1),
            end_date = datetime.date(2022, 10,21),
        )


    def _assert_student_is_valid(self):
        try:
            self.term.full_clean()
        except(ValidationError):
            self.fail('Test term should be valid')

    def _assert_student_is_invalid(self):
        with self.assertRaises(ValidationError):
            self.term.full_clean()


    #tests for students name
    def test_term_number_must_not_be_blank(self):
        self.term.term_number = ''
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


    #tests for student email
    def test_email_must_not_be_blank(self):
        self.student.email = ''
        self._assert_student_is_invalid()

    def test_email_must_be_unique(self):
        second_student = self._create_second_student()
        self.student.email = second_student.email
        self._assert_student_is_invalid()


    def test_student_is_valid(self):
        self._assert_student_is_valid()

