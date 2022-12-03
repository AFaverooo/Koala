"""Unit tests of the user form."""
from django.contrib.auth.hashers import check_password
from django import forms
from django.test import TestCase
from lessons.forms import CreateAdminForm
from lessons.models import UserAccount,UserRole,Gender

class UserFormTestCase(TestCase):
    """Unit tests of the create admins form."""

    def setUp(self):
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.org',
            'gender': 'F',
            'new_password': 'Password123',
            'password_confirmation': 'Password123',
        }

    def test_valid_sign_up_form(self):
        form = CreateAdminForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form = CreateAdminForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('gender', form.fields)
        self.assertIn('email', form.fields)
        email_field = form.fields['email']
        self.assertTrue(isinstance(email_field, forms.EmailField))
        self.assertIn('new_password', form.fields)
        new_password_widget = form.fields['new_password'].widget
        self.assertTrue(isinstance(new_password_widget, forms.PasswordInput))
        self.assertIn('password_confirmation', form.fields)
        password_confirmation_widget = form.fields['password_confirmation'].widget
        self.assertTrue(isinstance(password_confirmation_widget, forms.PasswordInput))

    def test_password_must_contain_uppercase_character(self):
        self.form_input['new_password'] = 'password123'
        self.form_input['password_confirmation'] = 'password123'
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_lowercase_character(self):
        self.form_input['new_password'] = 'PASSWORD123'
        self.form_input['password_confirmation'] = 'PASSWORD123'
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_password_must_contain_number(self):
        self.form_input['new_password'] = 'PasswordABC'
        self.form_input['password_confirmation'] = 'PasswordABC'
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_new_password_and_password_confirmation_are_identical(self):
        self.form_input['password_confirmation'] = 'WrongPassword123'
        form = CreateAdminForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = CreateAdminForm(data=self.form_input)
        before_count = UserAccount.objects.count()
        form.save()
        after_count = UserAccount.objects.count()
        self.assertEqual(after_count, before_count+1)
        student = UserAccount.objects.get(email ='janedoe@example.org')
        self.assertEqual(student.first_name, 'Jane')
        self.assertEqual(student.last_name, 'Doe')
        self.assertEqual(student.gender, Gender.FEMALE.value)
        is_password_correct = check_password('Password123', student.password)
        self.assertTrue(is_password_correct)
