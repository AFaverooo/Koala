from django.test import TestCase
from lessons.models import Invoice

b = Invoice(reference_number= '111-11', student_number = '111', fees_amount=45)
b.save()

class invoiceTestCase(TestCase, Invoice): 

    def test_reference_must_not_be_blank(self):
        pass

    def test_reference_must_be_in_the_correct_form(test):
        pass