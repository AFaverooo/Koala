from django.conf import settings
from django.shortcuts import redirect
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender, Invoice, Transaction, InvoiceStatus,Term
from itertools import chain
from django.utils import timezone
import datetime

# Ensures user must log in before logging out (and redirects specific roles to their home page)

def login_prohibited(view_function):
    def modified_view_function(request):
        if request.user.is_authenticated:
            if (request.user.role == UserRole.STUDENT.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_STUDENT)
            elif (request.user.role == UserRole.ADMIN.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_ADMIN)
            elif (request.user.role == UserRole.DIRECTOR.value):
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN_DIRECTOR)
        else:
            return view_function(request)
    return modified_view_function

def check_valid_date(lesson_date):
    term_six_date = Term.objects.get(term_number = 6).end_date
    return lesson_date <= term_six_date
    
def get_saved_lessons(student):
    return get_student_and_child_lessons(student,LessonStatus.SAVED)

def get_admin_email():
    return UserAccount.objects.filter(role = UserRole.ADMIN).first()

def get_student_and_child_lessons(student, statusType):
    student_queryset = Lesson.objects.filter(lesson_status = statusType, student_id = student)

    if student.is_parent:
        child_queryset = UserAccount.objects.filter(parent_of_user = student)
        result_queryset = student_queryset

        for eachChild in child_queryset:
            lesson_queryset = Lesson.objects.filter(student_id = eachChild , lesson_status = statusType)
            result_queryset = chain(result_queryset, lesson_queryset)

        return list(result_queryset)

    return list(student_queryset)

def get_student_and_child_objects(student):
    list_of_students = []
    list_of_students.append(student)

    if student.is_parent is True:
        child_students = UserAccount.objects.filter(parent_of_user = student)

        for child in child_students:
            list_of_students.append(child)

    return list_of_students

def make_lesson_timetable_dictionary(student_user):
    fullfilled_lessons = get_student_and_child_lessons(student_user,LessonStatus.FULLFILLED)

    fullfilled_lessons_dict = {}

    if len(fullfilled_lessons) == 0:
        return fullfilled_lessons_dict

    for lesson in fullfilled_lessons:
        lesson_type_str = ''

        if lesson.type == LessonType.INSTRUMENT:
            lesson_type_str = LessonType.INSTRUMENT.label
        elif lesson.type == LessonType.THEORY:
            lesson_type_str = LessonType.THEORY.label
        elif lesson.type == LessonType.PRACTICE:
            lesson_type_str = LessonType.PRACTICE.label
        elif lesson.type == LessonType.PERFORMANCE:
            lesson_type_str = LessonType.PERFORMANCE.label


        new_time = lesson.lesson_date_time + datetime.timedelta(minutes=int(lesson.duration))

        new_lesson_hr_str = ''
        lesson_date_hr_str = ''

        new_time_minute_str = ''
        lesson_date_minute_str = ''

        #format minutes using :00 notation
        if new_time.minute < 10:
            new_time_minute_str = f'0{new_time.minute}'
        else:
            new_time_minute_str = f'{new_time.minute}'

        if lesson.lesson_date_time.minute < 10:
            lesson_date_minute_str = f'0{lesson.lesson_date_time.minute}'
        else:
            lesson_date_minute_str = f'{lesson.lesson_date_time.minute}'

        #format hours using 00: notation
        if new_time.hour < 10:
            new_lesson_hr_str = f'0{new_time.hour}'
        else:
            new_lesson_hr_str = f'{new_time.hour}'

        if lesson.lesson_date_time.hour < 10:
            lesson_date_hr_str = f'0{lesson.lesson_date_time.hour}'
        else:
            lesson_date_hr_str = f'{lesson.lesson_date_time.hour}'

        teacher_str = ''

        if lesson.teacher_id.gender == Gender.FEMALE:
            teacher_str = f'Miss {lesson.teacher_id}'
        elif lesson.teacher_id.gender == Gender.MALE:
            teacher_str = f'Mr {lesson.teacher_id}'
        else:
            teacher_str = f'{lesson.teacher_id}'

        duration_str = f'{lesson_date_hr_str}:{lesson_date_minute_str} - {new_lesson_hr_str}:{new_time_minute_str}'

        case = {'Student':lesson.student_id,'Lesson': f'{lesson_type_str}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson Duration': f'{duration_str}', 'Teacher': f'{teacher_str}'}
        fullfilled_lessons_dict[lesson] = case

    return fullfilled_lessons_dict

def make_lesson_dictionary(student_user,lessonStatus):
    lessons = []

    if lessonStatus == 'Lesson Request':
        lessons = get_student_and_child_lessons(student_user,LessonStatus.UNFULFILLED)

    lessons_dict = {}

    for lesson in lessons:
        temp_dict = {}

        request_date_str = lesson.request_date.strftime("%Y-%m-%d")

        if request_date_str not in lessons_dict.keys():
            lessons_dict[request_date_str] = []

        lesson_type_str = ''

        if lesson.type == LessonType.INSTRUMENT:
            lesson_type_str = LessonType.INSTRUMENT.name
        elif lesson.type == LessonType.THEORY:
            lesson_type_str = LessonType.THEORY.name
        elif lesson.type == LessonType.PRACTICE:
            lesson_type_str = LessonType.PRACTICE.name
        elif lesson.type == LessonType.PERFORMANCE:
            lesson_type_str = LessonType.PERFORMANCE.name

        lesson_duration_str = f'{lesson.duration} minutes'

        case = {'Student':lesson.student_id, lessonStatus: f'{lesson.lesson_id}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson': f'{lesson_type_str}', "Lesson Duration": f'{lesson_duration_str}', "Teacher": f'{lesson.teacher_id}'}
        temp_dict[lesson] = case

        lessons_dict[request_date_str].append(temp_dict)

    return lessons_dict
