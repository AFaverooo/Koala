from django.test import TestCase
from lessons.models import Invoice

b = Invoice(reference_number= '111-11', student_ID = '111', fees_amount=45)
b.save()

class invoiceTestCase(TestCase, Invoice): 

    def test_reference_must_not_be_blank(self):
        pass

    def test_reference_must_be_in_the_correct_form(test):
        pass

    def fees_cannot_be_0():
        pass

    def there_can_only_be_one_slush():
        pass