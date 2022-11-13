from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator,MaxValueValidator,MinValueValidator

#Student model refers to the User of the MSMS application
class Student(AbstractUser):
    student_ethinicity = models.CharField(max_length = 30, blank = False)
    student_gender = models.CharField(max_length = 20, blank = False)
    student_age = models.PositiveIntegerField(blank=False, validators = [MinValueValidator(18), MaxValueValidator(70)])
