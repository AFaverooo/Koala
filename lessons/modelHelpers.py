from .models import UserAccount, UserRole

def produce_teacher_object(email):
    for eachUser in UserAccount.objects.all():
        if (eachUser.email == email):
            return eachUser
