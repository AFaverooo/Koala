from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.contrib import messages

from .forms import LogInForm,SignUpForm,RequestForm,TermDatesForm,CreateAdminForm
from django.contrib.auth import authenticate,login,logout
from .models import UserRole, UserAccount, Lesson, LessonStatus, LessonType, Gender, Invoice, Transaction, InvoiceStatus,Term
from .helper import login_prohibited

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.db import IntegrityError
from django.utils import timezone
import datetime
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain


# Create your views here.

from django.template.defaulttags import register

@register.filter
def get_lesson_duration(dictionary):
    return dictionary.get("Lesson Duration")

@register.filter
def get_lesson(dictionary):
    return dictionary.get("Lesson")

@register.filter
def get_lesson_date(dictionary):
    return dictionary.get("Lesson Date")

@register.filter
def get_teacher(dictionary):
    return dictionary.get("Teacher")

@register.filter
def get_lesson_request(dictionary):
    return dictionary.get("Lesson Request")

@register.filter
def get_lesson_saved(dictionary):
    return dictionary.get("Saved")

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

        case = {'Lesson': f'{lesson_type_str}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson Duration': f'{duration_str}', 'Teacher': f'{teacher_str}'}
        fullfilled_lessons_dict[lesson] = case

    return fullfilled_lessons_dict

def make_lesson_dictionary(student_user,lessonStatus):
    lessons = []
    if lessonStatus == 'Lesson Request':
        lessons = get_student_and_child_lessons(student_user,LessonStatus.UNFULFILLED)
    else:
        lessons = get_saved_lessons(student_user)

    lessons_dict = {}

    id_count = 0
    for lesson in lessons:
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

        case = {lessonStatus: f'{id_count}', 'Lesson Date': f'{lesson.lesson_date_time.date()}', 'Lesson': f'{lesson_type_str}', "Lesson Duration": f'{lesson_duration_str}', "Teacher": f'{lesson.teacher_id}'}
        lessons_dict[lesson] = case
        id_count += 1

    return lessons_dict


@login_required
def balance(request):
    if(request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if request.method == 'GET':
            student = request.user
            student_invoice = get_student_invoice(student) #this function filter out the invocie with the same student id as the current user
            student_transaction = get_student_transaction(student) #this function filter out the transaction with the same student id as the current user
            update_balance(student)
            student_balance = get_student_balance(student)
            child_invoices =  get_child_invoice(student)
            return render(request, 'balance.html', {'student': student, 'Invoice': student_invoice, 'Transaction': student_transaction, 'Balance': student_balance, 'child_invoices': child_invoices})
    else:
        return redirect('home')

def get_student_invoice(student):
    return Invoice.objects.filter(student_ID = student.id)

def get_student_transaction(student):
    return Transaction.objects.filter( Student_ID_transaction = student.id)

def get_student_balance(student):
    return UserAccount.objects.filter(id = student.id).values_list('balance', flat=True)

def get_child_invoice(student):
    list_of_child_invoice = []

    children = UserAccount.objects.filter(parent_of_user = student)
    for child in children:
        child_invoice = Invoice.objects.filter(student_ID = child.id)
        for invoice in child_invoice:
            list_of_child_invoice.append(invoice)
    
    return list_of_child_invoice


# this function update the student balance
def update_balance(student):
    current_existing_invoice = Invoice.objects.filter(student_ID = student.id)
    current_existing_transaction = Transaction.objects.filter(Student_ID_transaction = student.id)
    child_invoices = get_child_invoice(student)
    invoice_fee_total = 0
    payment_fee_total = 0

    for invoice in current_existing_invoice:
        invoice_fee_total += invoice.fees_amount

    for child_invoice in child_invoices:
        invoice_fee_total += child_invoice.fees_amount

    for transaction in current_existing_transaction:
        payment_fee_total += transaction.transaction_amount

    student.balance = payment_fee_total - invoice_fee_total
    student.save()

@login_required
def pay_for_invoice(request):
    if(request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if(request.method == 'POST'):
            try:
                input_invoice_reference = request.POST.get('invocie_reference')
                input_amounts_pay = request.POST.get('amounts_pay')
                input_amounts_pay_int = int(input_amounts_pay)
            except ValueError:
                messages.add_message(request,messages.ERROR,"You cannot submit without enter a value!")
                return redirect('balance')

            student = request.user
            try:
                temp_invoice = Invoice.objects.get(reference_number = input_invoice_reference)
            except ObjectDoesNotExist:
                messages.add_message(request,messages.ERROR,"There isn't such invoice exist!")
                return redirect('balance')

            if(int(temp_invoice.student_ID) != int(student.id) and check_invoice_belong_to_child(temp_invoice, student) == False):
                messages.add_message(request,messages.ERROR,"this invoice does not belong to you or your children!")
            elif(temp_invoice.invoice_status == InvoiceStatus.PAID):
                messages.add_message(request,messages.ERROR,"This invoice has already been paid!")
            elif(temp_invoice.invoice_status == InvoiceStatus.DELETED):
                messages.add_message(request,messages.ERROR,"This invoice has already been deleted!")
            elif(input_amounts_pay_int < 1):
                messages.add_message(request,messages.ERROR,"Transaction amount cannot be less than 1!")
            elif(input_amounts_pay_int > 10000):
                messages.add_message(request,messages.ERROR,"Transaction amount cannot be larger than 10000!")
            else:
                if(temp_invoice.amounts_need_to_pay <= input_amounts_pay_int):
                    temp_invoice.invoice_status = InvoiceStatus.PAID
                    temp_invoice.amounts_need_to_pay = 0
                elif(temp_invoice.amounts_need_to_pay > input_amounts_pay_int):
                    temp_invoice.invoice_status = InvoiceStatus.PARTIALLY_PAID
                    temp_invoice.amounts_need_to_pay -= input_amounts_pay_int
                update_balance(student)
                student.save()
                temp_invoice.save()

                Transaction.objects.create(Student_ID_transaction = student.id, invoice_reference_transaction = input_invoice_reference, transaction_amount = input_amounts_pay_int)

            return redirect('balance')

        return redirect('balance')

    else:
        return redirect('home')

def check_invoice_belong_to_child(temp_invoice, student):
    children = UserAccount.objects.filter(parent_of_user = student)
    for child in children:
        if int(temp_invoice.student_ID) == int(child.id):
            return True
    return False


def create_new_invoice(student_id, lesson):
    student_number_of_invoice_pre_exist = Invoice.objects.filter(student_ID = student_id)
    student = UserAccount.objects.get(id=student_id)
    reference_number_temp = Invoice.generate_new_invoice_reference_number(str(student_id), len(student_number_of_invoice_pre_exist))
    lesson_duration = lesson.duration
    fees = Invoice.calculate_fees_amount(lesson_duration)
    fees = int(fees)
    Invoice.objects.create(reference_number =  reference_number_temp, student_ID = student_id, fees_amount = fees, invoice_status = InvoiceStatus.UNPAID, amounts_need_to_pay = fees, lesson_ID = lesson.lesson_id)
    update_balance(student)

def update_invoice(lesson):
    invoice = Invoice.objects.get(lesson_ID = lesson.lesson_id)
    student = UserAccount.objects.get(id=invoice.student_ID)

    fees = Invoice.calculate_fees_amount(lesson.duration)
    fees = int(fees)
    difference_between_invoice = fees - invoice.fees_amount
    invoice.fees_amount = fees
    invoice.amounts_need_to_pay += difference_between_invoice
    invoice.save()
    student = UserAccount.objects.get(id=invoice.student_ID)

    update_balance(student)

def update_invoice_when_delete(lesson):
    invoice = Invoice.objects.get(lesson_ID = lesson.lesson_id)
    invoice.invoice_status = InvoiceStatus.DELETED
    invoice.amounts_need_to_pay = 0
    invoice.fees_amount = 0
    invoice.lesson_ID = ''
    invoice.save()

def get_all_transactions(request):
    all_transactions = Transaction.objects.all()
    total = 0
    for each_transaction in all_transactions:
            total+= each_transaction.transaction_amount

    return render(request,'transaction_history.html', {'all_transactions': all_transactions, 'total':total})

def get_all_invocies(request):
    all_invoices = Invoice.objects.all()

    return render(request,'invoices_history.html', {'all_invoices': all_invoices})

def get_student_invoices_and_transactions(request, student_id):
    student = UserAccount.objects.get(id=student_id)
    all_invoices = Invoice.objects.filter(student_ID = student_id)
    all_transactions = Transaction.objects.filter(Student_ID_transaction = student_id)

    return render(request, 'student_invoices_and_transactions.html', {'student': student, 'all_invoices': all_invoices, 'all_transactions':all_transactions})

def get_student_and_child_objects(student):
    list_of_students = []
    list_of_students.append(student)

    if student.is_parent is True:
        child_students = UserAccount.objects.filter(parent_of_user = student)

        for child in child_students:
            list_of_students.append(child)

    return list_of_students

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

def get_saved_lessons(student):
    return get_student_and_child_lessons(student,LessonStatus.SAVED)

def get_unfulfilled_lessons(student):
    return Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED, student_id = student)

def get_fullfilled_lessons(student):
    return Lesson.objects.filter(lesson_status = LessonStatus.FULLFILLED, student_id = student)

def get_admin_email():
    return UserAccount.objects.filter(role = UserRole.ADMIN).first()

# Admin functionality view functions

def student_requests(request,student_id):
    saved_lessons = Lesson.objects.filter(student_id = student_id)
    student = UserAccount.objects.get(id=student_id)
    return render(request,'admin_student_requests_page.html',{'saved_lessons':saved_lessons, 'student': student})

def admin_update_request_page(request, lesson_id):
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        data = {
            'type' : lesson.type,
            'duration': lesson.duration,
            'lesson_date_time': lesson.lesson_date_time,
            'teachers' : lesson.teacher_id
            }
        form = RequestForm(data)
        return render(request,'admin_update_request.html', {'form': form , 'lesson': lesson})
    except ObjectDoesNotExist:
        messages.add_message(request, messages.SUCCESS, 'Lesson was successfully updated!')
        return redirect('admin_feed')

def admin_update_request(request, lesson_id):
    try:
        lesson = Lesson.objects.get(lesson_id=lesson_id)
        form = RequestForm(request.POST)

        if form.is_valid():
            type = form.cleaned_data.get('type')
            duration = form.cleaned_data.get('duration')
            lesson_date_time = form.cleaned_data.get('lesson_date_time')
            teacher_id = form.cleaned_data.get('teachers')

        if (lesson.type == type and lesson.duration == duration and lesson.lesson_date_time == lesson_date_time and lesson.teacher_id == teacher_id):
            messages.add_message(request, messages.ERROR, 'Lesson details are the same as before!')
            return render(request,'admin_update_request.html', {'form': form , 'lesson': lesson})
        else:
            lesson.type = type
            lesson.duration = duration
            lesson.lesson_date_time = lesson_date_time
            lesson.teacher_id = teacher_id
            lesson.save()

            update_invoice(lesson)

            messages.add_message(request, messages.SUCCESS, 'Lesson was successfully updated!')

            student = UserAccount.objects.get(id=lesson.student_id.id)
            return redirect('student_requests',student.id)

    except ObjectDoesNotExist:
        return redirect('admin_feed')

def admin_confirm_booking(request, lesson_id):
    lesson = Lesson.objects.get(lesson_id=lesson_id)
    if(lesson.lesson_status == 'BK'):
        messages.add_message(request, messages.INFO, 'Already booked!')
    else:
        lesson.lesson_status = 'BK'
        lesson.save()
        messages.add_message(request, messages.SUCCESS, 'Successfully Booked!')
        create_new_invoice(lesson.student_id.id, lesson)
    student = UserAccount.objects.get(id=lesson.student_id.id)
    return redirect('student_requests',student.id)

def delete_lesson(request, lesson_id):
    lesson = Lesson.objects.get(lesson_id=lesson_id)
    if lesson is not None:
        update_invoice_when_delete(lesson)
        lesson.delete()

        messages.add_message(request, messages.SUCCESS, 'Lesson was successfully deleted!')
        student = UserAccount.objects.get(id=lesson.student_id.id)
        return redirect('student_requests',student.id)


# Term view functions


def term_management_page(request):
    terms_list = Term.objects.all().order_by('term_number').values()
    return render(request,'term_management.html', {'terms_list': terms_list})

def add_term_page(request):
    if len(Term.objects.all()) < 6:
        form = TermDatesForm()
        return render(request, 'create_term_form.html', {'form':form})
    else:
        messages.add_message(request,messages.ERROR, "Cannot have more than 6 terms in a year, please edit or delete existing terms!")
        return term_management_page(request)

def create_term(request):
    form = TermDatesForm(request.POST)
    if form.is_valid():
        term_number = form.cleaned_data.get('term_number')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        # if(term_number!=1):

        doesTermNumberAlredyExist = None
        doesTermNumberAlredyExist = Term.objects.filter(term_number=term_number)
        if(doesTermNumberAlredyExist):
            messages.add_message(request, messages.ERROR, 'There already exists a term with this term number!')
            return render(request,'create_term_form.html', {'form': form})

        try:
            previous_term = Term.objects.get(term_number=str(int(term_number)-1))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "Previous term's numbers are missing, please rectify term numbers!")
            return render(request, 'create_term_form.html', {'form':form})

        if(start_date > end_date or end_date < start_date):
            messages.add_message(request, messages.ERROR, "This term's end date and start date overlap with one another!")
            return render(request, 'create_term_form.html', {'form':form})

        elif(start_date < previous_term.end_date):
            messages.add_message(request, messages.ERROR, "This term's start date overlaps with the previous term's ending date!")
            return render(request, 'create_term_form.html', {'form':form})

        form.save()
    else:
        messages.add_message(request,messages.ERROR, "Validator is set to only accept term numbers from 1 to 6!")
        return term_management_page(request)

    messages.add_message(request,messages.SUCCESS, "Successfully added term!")
    return term_management_page(request)


def edit_term_details_page(request,term_number):
    term = Term.objects.get(term_number=term_number)
    terms_list = Term.objects.all()
    # if( int(term_number)-1 >0 ):
    try:
        previous_term = Term.objects.get(term_number=str(int(term_number)-1))
    except ObjectDoesNotExist:
        previous_term = None
            # messages.add_message(request,messages.ERROR, f'Please ensure the previous term number ({int(term_number)-1}) is added before attempting to edit!')
            # return term_management_page(request)

    # if( int(term_number)+1 <len(terms_list) + 1 ):
    try:
        next_term = Term.objects.get(term_number=str(int(term_number)+1))
    except ObjectDoesNotExist:
        next_term = None
            # messages.add_message(request,messages.ERROR, f'Please ensure the next term number ({int(term_number)+1}) is added before attempting to edit!')
            # return term_management_page(request)

    data = {
        'term_number': term.term_number,
        'start_date': term.start_date,
        'end_date': term.end_date,
        }
    form = TermDatesForm(data)
    return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

def update_term_details(request,term_number):
    try:
        term = Term.objects.get(term_number=term_number)
        form = TermDatesForm(request.POST)

        if form.is_valid():
            term_number_in = form.cleaned_data.get('term_number')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')

        try:
            previous_term = Term.objects.get(term_number=str(int(term_number_in)-1))
        except ObjectDoesNotExist:#For when editing a lesson with term number 1
            previous_term = None

        try:
            next_term = Term.objects.get(term_number=str(int(term_number_in)+1))
        except ObjectDoesNotExist:#For when editing a lesson with a term number with no next term in database
            next_term = None

        doesTermNumberAlredyExist = None
        doesTermNumberAlredyExist = Term.objects.filter(term_number=term_number_in)
        if( doesTermNumberAlredyExist ):
            messages.add_message(request, messages.ERROR, 'There already exists a term with this term number!')
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

        if (term.start_date == start_date and term.end_date == end_date and term.term_number == term_number_in):
            #terms_list = Term.objects.all()
            messages.add_message(request, messages.ERROR, 'Term details are the same as before!')
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})



        if(next_term != None and end_date > next_term.start_date and term_number != term_number_in):
            messages.add_message(request, messages.ERROR, "Term's end date overlaps with the next term's start date for the chosen term number. Try changing the term number or fix term overlap before attempting to alter term number!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

        elif(previous_term != None and start_date < previous_term.end_date and term_number != term_number_in):
            messages.add_message(request, messages.ERROR, "Term's start date overlaps with the previous term's end date for the chosen term number. Try changing the term number or fix term overlap before attempting to alter term number!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})



        if(start_date > end_date or end_date < start_date):
            messages.add_message(request, messages.ERROR, "This term's end date and start date overlap with one another!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

        elif(previous_term !=None and next_term !=None  and end_date > next_term.start_date and start_date < previous_term.end_date):
            messages.add_message(request, messages.ERROR, "This term's end date and start date overlap with other terms!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})


        elif(next_term !=None and end_date > next_term.start_date):
            messages.add_message(request, messages.ERROR, "This term's end date overlaps with the next term's starting date!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

        elif(previous_term !=None and start_date < previous_term.end_date):
            messages.add_message(request, messages.ERROR, "This term's start date overlaps with the previous term's ending date!")
            return render(request,'edit_term_form.html', {'form': form, 'term':term,'previous_term':previous_term,'next_term':next_term})

        term.term_number = term_number_in
        term.start_date = start_date
        term.end_date = end_date
        term.save()
        messages.add_message(request, messages.SUCCESS, 'Term details were successfully updated!')

        return term_management_page(request)

    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, 'The input data is invalid (Term number must be 1-6)')
        return term_management_page(request)


def delete_term(request, term_number):
    term = Term.objects.get(term_number=term_number)
    if term is not None:
        term.delete()
        messages.add_message(request, messages.SUCCESS, 'Term was successfully deleted!')
        return term_management_page(request)




@login_required
def student_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if request.method == 'GET':
            unfulfilled_lessons = get_unfulfilled_lessons(request.user)
            fullfilled_lessons = get_fullfilled_lessons(request.user)

            greeting_str = f'Welcome back {request.user}, this is your feed!'

            fullfilled_lessons = make_lesson_timetable_dictionary(request.user)
            unfulfilled_requests = make_lesson_dictionary(request.user,"Lesson Request")

            admin = get_admin_email()

            admin_email_str = ''

            if admin:
                admin_email_str = f'To Further Edit Bookings Contact {admin.email}'
            else:
                admin_email_str = f'No Admins Available To Contact'

            return render(request,'student_feed.html', {'admin_email': admin_email_str,'unfulfilled_requests':unfulfilled_requests, 'fullfilled_lessons':fullfilled_lessons, 'greeting':greeting_str})
        else:
            return HttpResponseForbidden()
    else:
        # return redirect('log_in')
        return redirect('home')

@login_required
def requests_page(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        if request.method == 'GET':
            student = request.user
            students_option = get_student_and_child_objects(student)
            savedLessons = get_saved_lessons(student)
            form = RequestForm()
            return render(request,'requests_page.html', {'form': form , 'lessons': savedLessons, 'students_option':students_option})
        else:
            return HttpResponseForbidden()
    else:
        return redirect('home')

@login_required
def admin_feed(request):

    if (request.user.is_authenticated and request.user.role == UserRole.ADMIN):
        student = UserAccount.objects.filter(role=UserRole.STUDENT.value)
        fulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.FULLFILLED)
        unfulfilled_lessons = Lesson.objects.filter(lesson_status = LessonStatus.UNFULFILLED)
        return render(request,'admin_feed.html',{'student':student,'fulfilled_lessons':fulfilled_lessons,'unfulfilled_lessons':unfulfilled_lessons})
    else:
        # return redirect('log_in')
        return redirect('home')

@login_required
def director_feed(request):
    if (request.user.is_authenticated and request.user.role == UserRole.DIRECTOR):
        return render(request,'director_feed.html')
    else:
        # return redirect('log_in')
        return redirect('home')


@login_required
def director_manage_roles(request):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        students = UserAccount.objects.filter(role = UserRole.STUDENT)
        teachers = UserAccount.objects.filter(role = UserRole.TEACHER)
        admins = UserAccount.objects.filter(role = UserRole.ADMIN)
        directors = UserAccount.objects.filter(role = UserRole.DIRECTOR)
        return render(request,'director_manage_roles.html',{'students':students, 'teachers':teachers, 'admins':admins, 'directors':directors})
    else:
        return redirect("home")



@login_required
def promote_director(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot promote yourself!")
            return redirect('director_manage_roles')
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.role = UserRole.DIRECTOR
            user.is_staff = True
            user.is_superuser = True
            user.save()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} now has the role director")
            return redirect('director_manage_roles')
    else:
        return redirect("home")


@login_required
def promote_admin(request,current_user_email):

    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot demote yourself!")
            return redirect('director_manage_roles')
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.role = UserRole.ADMIN
            user.is_staff = True
            user.is_superuser = False
            user.save()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} now has the role admin")
            return redirect("director_manage_roles")
    else:

        return redirect("home")



@login_required
def disable_user(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot disable yourself!")
            return redirect(director_manage_roles)
        else:
            user = UserAccount.objects.get(email=current_user_email)
            if (user.is_active == True):
                user.is_active = False
                user.save()
                messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly disabled!")
            else:
                user.is_active = True
                user.save()
                messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly enabled!")

            return redirect(director_manage_roles)
    else:
        return redirect("home")



@login_required
def delete_user(request,current_user_email):
    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        if (request.user.email == current_user_email):
            messages.add_message(request,messages.ERROR,"You cannot delete yourself!")
            return redirect(director_manage_roles)
        else:
            user = UserAccount.objects.get(email=current_user_email)
            user.delete()
            messages.add_message(request,messages.SUCCESS,f"{current_user_email} has been sucessfuly deleted!")
            return redirect(director_manage_roles)
    else:
        return redirect("home")



def create_admin_page(request):

    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:

        if request.method == 'POST':
            form = CreateAdminForm(request.POST)
            if form.is_valid():
                admin = form.save()
                return redirect('director_manage_roles')
        else:
            form = CreateAdminForm()

        return render(request,'director_create_admin.html',{'form': form})
    else:
        return redirect("home")


@login_required
def update_user(request,current_user_id):

    if request.user.is_authenticated and request.user.role == UserRole.DIRECTOR:
        user = UserAccount.objects.get(id=current_user_id)
        form = CreateAdminForm(instance=user)

        if request.method == 'POST':
            form = CreateAdminForm(request.POST, instance = user)
            if form.is_valid():
                email = form.cleaned_data.get('email')
                fname = form.cleaned_data.get('first_name')
                lname = form.cleaned_data.get('last_name')
                gender = form.cleaned_data.get('gender')

                new_password = form.cleaned_data.get('new_password')

                user.email = email
                user.first_name = fname
                user.last_name = lname
                user.gender = gender

                user.set_password(new_password)
                user.save()

                # current user logged out if he edits himself
                if (int(request.user.id) == int(current_user_id)):
                    messages.add_message(request,messages.SUCCESS,f"You cant't edit yourself!")
                    return log_out(request)

                messages.add_message(request,messages.SUCCESS,f"{user.email} has been sucessfuly updated!")
                return redirect('director_manage_roles')

        return render(request,'director_update_user.html', {'form': form , 'user': user})


@login_prohibited
def home(request):
    if request.method == 'POST':
        form = LogInForm(request.POST)
        email = request.POST.get("email")
        password = request.POST.get("password")
        if  form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            role = form.cleaned_data.get('role')
            user = authenticate(email=email, password=password)
            if user is not None:
                login(request,user)

                 # redirects the user based on his role
                if (user.role == UserRole.ADMIN.value):
                     #redirect_url = request.POST.get('next') or 'admin_feed'
                    return redirect('admin_feed')
                elif (user.role == UserRole.DIRECTOR.value):
                    redirect_url = request.POST.get('next') or 'director_feed'
                    return redirect(redirect_url)
                else:
                    redirect_url = request.POST.get('next') or 'student_feed'
                    return redirect(redirect_url)

        messages.add_message(request,messages.ERROR,"The credentials provided is invalid!")
    form = LogInForm()
    next = request.GET.get('next') or ''
    #return render(request,'log_in.html', {'form' : form, 'next' : next})
    return render(request,'home.html', {'form' : form, 'next' : next})


def log_out(request):
    logout(request)
    return redirect('home')

def sign_up_child(request):
    if request.user.is_authenticated and request.user.role == UserRole.STUDENT:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                student = form.save_child(request.user)
                return redirect('student_feed')
        else:
            form = SignUpForm()
        return render(request, 'sign_up_child.html', {'form': form})
    else:
        return redirect('home')

@login_prohibited
def sign_up(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            student = form.save()
            login(request, student)
            return redirect('student_feed')
    else:
        form = SignUpForm()
    return render(request, 'sign_up.html', {'form': form})

def new_lesson(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        #current_student = request.user

        if request.method == 'POST':
            request_form = RequestForm(request.POST)
            if request_form.is_valid():

                try:
                    actual_student = UserAccount.objects.get(email = request.POST['selectedStudent'])
                except ObjectDoesNotExist:
                    messages.add_message(request,messages.ERROR,"Selected user account does not exist")
                    students_option = get_student_and_child_objects(request.user)
                    return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(request.user), 'students_option':students_option})
                #duration = request_form.cleaned_data.get('duration')
                #lesson_date = request_form.cleaned_data.get('lesson_date_time')
                #type = request_form.cleaned_data.get('type')
                #teacher_id = request_form.cleaned_data.get('teachers')

                try:
                    request_form.save(actual_student)#Lesson.objects.create(type = type, duration = duration, lesson_date_time = lesson_date, teacher_id = teacher_id, student_id = current_student)
                except IntegrityError:
                    messages.add_message(request,messages.ERROR,"Lesson information provided already exists")
                    students_option = get_student_and_child_objects(request.user)
                    return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(request.user), 'students_option':students_option})

                #form = RequestForm()
                #return render(request,'requests_page.html', {'form' : form , 'lessons': get_saved_lessons(current_student)})
                messages.add_message(request,messages.SUCCESS,"Lesson has been created")
                return redirect('requests_page')
            else:
                messages.add_message(request,messages.ERROR,"The lesson information provided is invalid!")
                students_option = get_student_and_child_objects(request.user)
                return render(request,'requests_page.html', {'form' : request_form , 'lessons': get_saved_lessons(request.user), 'students_option':students_option})
        else:
            #form = RequestForm()
            #return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
            return redirect('requests_page')

    else:
        return redirect('home')

#make it that all lessons for both the student and if they have a child
def save_lessons(request):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        current_student = request.user
        if request.method == 'POST':
            all_unsaved_lessons = get_saved_lessons(current_student)

            if len(all_unsaved_lessons) == 0:
                messages.add_message(request,messages.ERROR,"Lessons should be requested before attempting to save")
                return redirect('requests_page')

            for eachLesson in all_unsaved_lessons:
                eachLesson.lesson_status = LessonStatus.UNFULFILLED
                eachLesson.save()

            messages.add_message(request,messages.SUCCESS, "Lesson requests are now pending for validation by admin")
            return redirect('student_feed')
        else:
            #form = RequestForm()
            #return render(request,'requests_page.html', {'form' : form ,'lessons': get_saved_lessons(current_student)})
            return redirect('requests_page')
    else:
        #print('user should be logged in')
        return redirect('home')
        #form = RequestForm()
        #return render(rquest,'requests_page.html', {'form':form})
def check_correct_student_accessing_lesson(student_id, other_lesson):
    all_student_lessons = Lesson.objects.filter(student_id = student_id, lesson_status = LessonStatus.UNFULFILLED)
    for lesson in all_student_lessons:
        if lesson.is_equal(other_lesson):
            return True

    return False

def render_edit_request(request,lesson_id):
    try:
        to_edit_lesson = Lesson.objects.get(lesson_id = int(lesson_id)) #used to be lesson_lesson_edit_id from get method
    except ObjectDoesNotExist:
        messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
        return redirect('student_feed')

    data = {'type': to_edit_lesson.type,
            'duration': to_edit_lesson.duration,
            'lesson_date_time': to_edit_lesson.lesson_date_time,
            'teachers': to_edit_lesson.teacher_id}

    form = RequestForm(data)
    return render(request,'edit_request.html', {'form' : form, 'lesson_id':lesson_id})


def edit_lesson(request,lesson_id):
    if (request.user.is_authenticated and request.user.role == UserRole.STUDENT):
        current_student = request.user

        try:
            to_edit_lesson = Lesson.objects.get(lesson_id = int(lesson_id))
        except ObjectDoesNotExist:
            messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
            return redirect('student_feed')

        if check_correct_student_accessing_lesson(current_student,to_edit_lesson) is False:
            messages.add_message(request, messages.WARNING, "Attempted Edit Is Not Permitted")
            return redirect('student_feed')

        if request.method == 'POST':
            request_form = RequestForm(request.POST)

            if request_form.is_valid():
                try:
                    request_form.update_lesson(to_edit_lesson)
                except IntegrityError:
                    messages.add_message(request,messages.ERROR,"Duplicate lessons are not allowed")
                    return render_edit_request(request,lesson_id)
                    #print('attempted to duplicate lesson')

                messages.add_message(request,messages.SUCCESS,"Succesfully edited lesson")
                return redirect('student_feed')
            else:
                messages.add_message(request,messages.ERROR,"Form is not valid")
                return render_edit_request(request,lesson_id)
        else:
            return render_edit_request(request,lesson_id)
    else:
        # return redirect('log_in')
        return redirect('home')

def delete_pending(request,lesson_id):
    if request.user.is_authenticated and request.user.role == UserRole.STUDENT:
        current_student = request.user
        #if check_correct_student_accessing_lesson(current_student,lesson_id):
        if request.method == 'POST':
                try:
                    lesson_to_delete = Lesson.objects.get(lesson_id = int(lesson_id))
                except ObjectDoesNotExist:
                    messages.add_message(request, messages.ERROR, "Incorrect lesson ID passed")
                    return redirect('student_feed')

                if check_correct_student_accessing_lesson(current_student,lesson_to_delete) is False:
                    messages.add_message(request, messages.WARNING, "Attempted Deletion Not Permitted")
                    return redirect('student_feed')

                lesson_to_delete.delete()
                messages.add_message(request, messages.SUCCESS, "Lesson request deleted")
                return redirect('student_feed')

        else:
            return redirect('student_feed')
    else:
        # return redirect('log_in')
        return redirect('home')
