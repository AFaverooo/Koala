"""Unit tests for the Invoice model"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from lessons.models import Invoice, InvoiceStatus

class InvoiceModelTestCase(TestCase):

    def setUp(self):
        self.invoice = Invoice.objects.create(
            reference_number = '111-001',
            student_ID = '111',
            fees_amount = '78',
            invoice_status = InvoiceStatus.UNPAID,
        )

    def _create_paid_invoice(self):
        invoice = Invoice.objects.create(
            reference_number = '222-012',
            student_ID = '222',
            fees_amount = '85',
            invoice_status = InvoiceStatus.PAID,
            
        )
        return invoice

    def _assert_invoice_is_valid(self):
        try:
            self.invoice.full_clean()
        except(ValidationError):
            self.fail('Test invoice should be valid')

    def _assert_invoice_is_invalid(self):      
        with self.assertRaises(ValidationError):
            self.invoice.full_clean()


    def test_valid_invoice(self):
        self._assert_invoice_is_valid()



    def test_reference_number_cannot_be_blank(self):
        self.invoice.reference_number = ''
        self._assert_invoice_is_invalid()

    def test_reference_number_can_be_30_characters_long(self):
        self.invoice.reference_number = '4' *14 + '-' + '5'*15
        self._assert_invoice_is_valid()

    def test_reference_number_cannot_be_over_30_characters_long(self):
        self.invoice.reference_number = '4' *14 + '-' + '5'*16
        self._assert_invoice_is_invalid()

    def test_reference_number_must_be_unique(self):
        second_invoice = self._create_paid_invoice()
        self.invoice.reference_number = second_invoice.reference_number
        self._assert_invoice_is_invalid()

    def test_reference_number_must_contain_hyphen_symbol_in_between(self):
        self.invoice.reference_number = '333344444'
        self._assert_invoice_is_invalid()

    def test_reference_number_must_contain_at_least_one_number_before_hyphen(self):
        self.invoice.reference_number = '-333344444'
        self._assert_invoice_is_invalid()

    def test_reference_number_must_contain_at_least_three_numbers_after_hyphen(self):
        self.invoice.reference_number = '3333-44'
        self._assert_invoice_is_invalid()

    def test_reference_number_must_contain_only_number_and_hyphen(self):
        self.invoice.reference_number = '33a-444'
        self._assert_invoice_is_invalid()

    



