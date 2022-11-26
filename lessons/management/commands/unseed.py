from django.core.management.base import BaseCommand, CommandError
from faker import Faker
from lessons.models import UserAccount, Invoice

class Command(BaseCommand):
    # Delete all users, except for email admin@example.org
    def handle(self, *args, **options):
        users = UserAccount.objects.all()
        for i in range(len(users)):

            if users[i].email != "admin@example.org":
                users[i].delete()

        invoices = Invoice.objects.all()
        for i in range(len(invoices)):
            invoices[i].delete()
