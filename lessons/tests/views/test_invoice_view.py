from django.test import TestCase
from lessons.models import Invoice, InvoiceStatus, UserAccount, Gender
from django.urls import reverse

class InvoiceTestCase(TestCase): 
    '''Tests of the invoice view'''

    def setUp(self):
        self.url = reverse('invoice')

        self.student = UserAccount.objects.create_student(
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org',
            password='Password123',
            gender = Gender.MALE,
        )

        self.invoice = Invoice.objects.create(
            reference_number = '111-001',
            student_ID = '111',
            fees_amount = '78',
            invoice_status = InvoiceStatus.UNPAID,
        )
        self.invoice = Invoice.objects.get(reference_number = '111-001')

    def test_invoice_url(self):
        self.assertEqual(self.url, '/invoice/')

    def test_get_invoice(self):
        self.client.login(username=self.student.email, password='Password123')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'invoice.html')





