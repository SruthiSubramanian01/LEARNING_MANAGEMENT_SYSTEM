from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm,TeacherRegistrationForm,LoginForm,TeacherEditForm,StudentEditForm,AttendanceEditForm
from django.http import JsonResponse
from django.db.models import Q,Sum,Count,Avg
from .models import User,Attendance,Assignment,Result,Notice,StudyMaterial,CareerApplication,Feedback,AssignmentSubmission,FeePayment,FeeStructure
from .forms import AttendanceForm,AssignmentForm,ResultForm,StudyMaterialForm,CareerApplicationForm,NoticeForm,FeedbackForm,GradeAssignmentForm,AssignmentSubmissionForm,FeePaymentForm,FeeStructureForm
from datetime import date
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.urls import reverse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
# Create your views here.
def homepage(request):
    return render(request,'home.html')
def aboutpage(request):
    return render(request,'about.html')
def coursespage(request):
    return render(request,'courses.html')
def contactpage(request):
    return render(request,'contact.html')
def gallerypage(request):
    return render(request,'gallery.html')
def teampage(request):
    return render(request,'team.html')

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'student'
            user.student_class = form.cleaned_data['student_class']
            user.status = 'pending'
            user.save()
            return render(request, 'pending_approval.html')
    else:
        form = StudentRegistrationForm()
    return render(request, 'student_register.html', {'form': form})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'teacher'
            user.qualification = form.cleaned_data['qualification']
            user.subject = form.cleaned_data['subject']
            user.status = 'pending'
            user.save()
            return render(request, 'pending_approval.html')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'teacher_register.html', {'form': form})

# ------------------------
# LOGIN VIEW
# ------------------------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                # Only allow login if approved or superuser
                if user.is_superuser or user.status == 'approved':
                    login(request, user)

                    # Redirect based on role
                    if user.is_superuser:
                        return redirect('admin_dashboard')
                    elif user.role == 'student':
                        return redirect('student_dashboard')
                    elif user.role == 'teacher':
                        return redirect('teacher_dashboard')
                    else:
                        return redirect('home')  # fallback
                else:
                    messages.error(
                        request,
                        'Your account is pending approval or has been rejected.'
                    )
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

# ------------------------
# LOGOUT VIEW
# ------------------------

@require_POST
@csrf_protect
def logout_view(request):
    """
    Professional logout view that handles both GET and POST requests securely.
    Clears session data and provides appropriate feedback to the user.
    """
    if request.user.is_authenticated:
        # Store username for message before logging out
        username = request.user.username
        
        # Clear any session data if needed
        # request.session.flush()  # Alternative: completely flush session
        
        # Perform logout
        logout(request)
        
        # Success message
        messages.success(request, f"You have been successfully logged out, {username}. We hope to see you again soon!")
    else:
        messages.info(request, "You were not logged in.")
    
    # Redirect to login page or homepage
    return redirect('login')

# ------------------------
# ADMIN DASHBOARD
# ------------------------
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        return redirect('home')

    pending_users = User.objects.filter(status='pending')
    approved_users = User.objects.filter(status='approved')
    rejected_users = User.objects.filter(status='rejected')

    teachers_count = User.objects.filter(role='teacher', status='approved').count()
    students_count = User.objects.filter(role='student', status='approved').count()
    pending_count = pending_users.count()

    context = {
        'pending_users': pending_users,
        'approved_users': approved_users,
        'rejected_users': rejected_users,
        'teachers_count': teachers_count,
        'students_count': students_count,
        'pending_count': pending_count,
    }
    return render(request, 'admin_dashboard.html', context)

def pending_approval(request):
    return render(request, 'pending_approval.html')

# ------------------------
# APPROVE / REJECT USERS
# ------------------------

@login_required
def approve_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user.status = 'approved'
    user.save()
    
    # Send approval email
    try:
        subject = 'Your Account Has Been Approved - Wisdom Learning Academy'
        
        # Get current site domain
        current_site = Site.objects.get_current()
        domain = current_site.domain
        
        # Build login URL
        login_url = f"http://{domain}{reverse('login')}"
        
        # Determine role display name
        role_display = user.get_role_display()
        
        # Render email templates
        html_message = render_to_string('email/account_approved.html', {
            'user': user,
            'role': role_display,
            'login_url': login_url,
        })
        
        plain_message = render_to_string('email/account_approved.txt', {
            'user': user,
            'role': role_display,
            'login_url': login_url,
        })
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        
        messages.success(request, f'{user.username} has been approved. Notification email sent to {user.email}.')
        
    except Exception as e:
        messages.warning(request, f'{user.username} has been approved, but email notification failed: {str(e)}')
    
    return redirect('admin_dashboard')

def test_email_setup(request):
    """Test view to verify email configuration is working"""
    try:
        # Send a test email to yourself
        send_mail(
            subject='Test Email - Wisdom Learning Academy',
            message='This is a test email to verify your email configuration is working properly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['sruthisubramanian3601@gmail.com'],  # Send to yourself first
            fail_silently=False,
        )
        messages.success(request, 'Test email sent successfully! Check your inbox.')
    except Exception as e:
        messages.error(request, f'Email test failed: {str(e)}')
    
    return redirect('admin_dashboard')

@login_required
def reject_user(request, user_id):
    if not request.user.is_superuser:
        return redirect('home')

    user = get_object_or_404(User, id=user_id)
    user.status = 'rejected'
    user.save()
    
    # Send rejection email
    try:
        subject = 'Your Account Application - Wisdom Learning Academy'
        current_site = Site.objects.get_current()
        domain = current_site.domain
        
        html_message = render_to_string('email/account_rejected.html', {
            'user': user,
            'role': user.get_role_display(),
            'domain': domain,
        })
        
        plain_message = render_to_string('email/account_rejected.txt', {
            'user': user,
            'role': user.get_role_display(),
            'domain': domain,
        })
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
            html_message=html_message
        )
        messages.success(request, f'{user.username} has been rejected. Notification email sent.')
    except Exception as e:
        messages.success(request, f'{user.username} has been rejected, but email notification failed: {str(e)}')
    
    return redirect('admin_dashboard')

# ------------------------
# STUDENT DASHBOARD
# ------------------------
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('home')
    return render(request, 'student_dashboard.html')

# ------------------------
# SIMPLE HOME VIEW
# ------------------------
def home(request):
    return render(request, 'home.html')

@login_required
def pending_requests(request):
    if not request.user.is_superuser:
        return redirect('home')

    pending_users = User.objects.filter(status='pending')
    return render(request, 'pending_requests.html', {'pending_users': pending_users})

@login_required
def manage_teachers(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    approved_teachers = User.objects.filter(role='teacher', status='approved')
    return render(request, 'manage_teachers.html', {'teachers': approved_teachers})

@login_required
def edit_teacher(request, teacher_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, f'Teacher {teacher.username} updated successfully!')
            return redirect('manage_teachers')
    else:
        form = TeacherEditForm(instance=teacher)
    
    return render(request, 'edit_teacher.html', {'form': form, 'teacher': teacher})

@login_required
def delete_teacher(request, teacher_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    
    if request.method == 'POST':
        username = teacher.username
        teacher.delete()
        messages.success(request, f'Teacher {username} deleted successfully!')
        return redirect('manage_teachers')
    
    return render(request, 'delete_teacher.html', {'teacher': teacher})


@login_required
def manage_students(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    approved_students = User.objects.filter(role='student', status='approved')
    return render(request, 'manage_students.html', {'students': approved_students})

@login_required
def edit_student(request, student_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    if request.method == 'POST':
        form = StudentEditForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, f'Student {student.username} updated successfully!')
            return redirect('manage_students')
    else:
        form = StudentEditForm(instance=student)
    
    return render(request, 'edit_student.html', {'form': form, 'student': student})

@login_required
def delete_student(request, student_id):
    if not request.user.is_superuser:
        return redirect('home')
    
    student = get_object_or_404(User, id=student_id, role='student')
    
    if request.method == 'POST':
        username = student.username
        student.delete()
        messages.success(request, f'Student {username} deleted successfully!')
        return redirect('manage_students')
    
    return render(request, 'delete_student.html', {'student': student})

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher' or request.user.status != 'approved':
        return redirect('home')
    
    # You can add any teacher-specific data here
    context = {
        'user': request.user,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def teacher_dashboard(request):
    if request.user.role != 'teacher' or request.user.status != 'approved':
        return redirect('home')
    
    # Get notices from admin
    notices = Notice.objects.all().order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'notices': notices,
    }
    return render(request, 'teacher_dashboard.html', context)

@login_required
def take_attendance(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            class_name = form.cleaned_data['class_name']
            date = form.cleaned_data['date']
            
            # Convert date to string format for template
            date_str = date.strftime('%Y-%m-%d')
            
            students = User.objects.filter(role='student', student_class=class_name, status='approved')
            
            # Check if attendance already exists for this date and class
            existing_attendance = Attendance.objects.filter(
                date=date, 
                class_name=class_name
            ).first()
            
            return render(request, 'mark_attendance.html', {
                'class_name': class_name,
                'date': date_str,
                'students': students,
                'existing_attendance': existing_attendance
            })
    else:
        form = AttendanceForm()
    
    return render(request, 'take_attendance.html', {'form': form})

@login_required
def upload_assignment(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    if request.method == 'POST':
        form = AssignmentForm(request.POST, request.FILES)
        if form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.subject = request.user.subject  # Auto-fill teacher's subject
            assignment.save()
            messages.success(request, 'Assignment uploaded successfully!')
            return redirect('teacher_dashboard')
    else:
        form = AssignmentForm(initial={'subject': request.user.subject})
    
    return render(request, 'upload_assignment.html', {'form': form})

@login_required
def upload_marks(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    if request.method == 'POST':
        form = ResultForm(request.POST)
        if form.is_valid():
            result = form.save(commit=False)
            result.uploaded_by = request.user
            result.save()
            messages.success(request, f'Marks for {result.student.get_full_name()} uploaded successfully!')
            return redirect('upload_marks')
    else:
        form = ResultForm(initial={'subject': request.user.subject})
    
    # Get recent results uploaded by this teacher
    recent_results = Result.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')[:5]
    
    return render(request, 'upload_marks.html', {
        'form': form,
        'recent_results': recent_results
    })

@login_required
def admin_manage_results(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Get filter parameters
    class_name = request.GET.get('class_name', '')
    subject = request.GET.get('subject', '')
    
    results = Result.objects.all().select_related('student', 'uploaded_by')
    
    # Apply filters
    if class_name:
        results = results.filter(class_name=class_name)
    if subject:
        results = results.filter(subject__iexact=subject)
    
    # Get unique values for dropdowns
    class_choices = [('', 'All Classes')] + list(User.CLASS_CHOICES)
    
    # Get unique subjects from database
    subjects = Result.objects.values_list('subject', flat=True).distinct()
    subject_choices = [('', 'All Subjects')] + [(s, s) for s in subjects]
    
    # Calculate statistics and add percentage to each result
    total_results = results.count()
    average_marks = results.aggregate(Avg('marks'))['marks__avg'] or 0
    
    # Add percentage to each result object for template display
    for result in results:
        try:
            result.percentage = (result.marks / result.total_marks) * 100
        except (ZeroDivisionError, TypeError):
            result.percentage = 0
        
        # Add grade based on percentage
        if result.percentage >= 90:
            result.grade = 'A+'
            result.grade_class = 'success'
        elif result.percentage >= 75:
            result.grade = 'A'
            result.grade_class = 'primary'
        elif result.percentage >= 60:
            result.grade = 'B'
            result.grade_class = 'info'
        elif result.percentage >= 40:
            result.grade = 'C'
            result.grade_class = 'warning'
        else:
            result.grade = 'F'
            result.grade_class = 'danger'
    
    context = {
        'results': results.order_by('class_name', 'student__first_name'),
        'total_results': total_results,
        'average_marks': round(average_marks, 2),
        'selected_class': class_name,
        'selected_subject': subject,
        'class_choices': class_choices,
        'subject_choices': subject_choices,
    }
    
    return render(request, 'admin_manage_results.html', context)

@login_required
def admin_delete_result(request, result_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can delete results.')
        return redirect('home')
    
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        student_name = result.student.get_full_name()
        subject = result.subject
        result.delete()
        messages.success(request, f'Result for {student_name} in {subject} deleted successfully!')
        return redirect('admin_manage_results')
    
    return render(request, 'admin_delete_result.html', {'result': result})

@login_required
def student_view_results(request):
    if request.user.role != 'student':
        return redirect('home')
    
    results = Result.objects.filter(student=request.user).order_by('subject')
    
    # Calculate overall statistics
    total_subjects = results.count()
    total_marks = results.aggregate(Sum('marks'))['marks__sum'] or 0
    total_max_marks = results.aggregate(Sum('total_marks'))['total_marks__sum'] or 0
    overall_percentage = (total_marks / total_max_marks * 100) if total_max_marks > 0 else 0
    
    # Calculate subject-wise averages
    subject_stats = []
    for result in results:
        subject_stats.append({
            'subject': result.subject,
            'marks': result.marks,
            'total_marks': result.total_marks,
            'percentage': result.percentage(),
            'grade': result.grade()
        })
    
    context = {
        'results': results,
        'total_subjects': total_subjects,
        'total_marks': total_marks,
        'total_max_marks': total_max_marks,
        'overall_percentage': round(overall_percentage, 2),
        'subject_stats': subject_stats,
    }
    
    return render(request, 'student_view_results.html', context)

@login_required
def teacher_view_results(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    # Get results uploaded by this teacher
    results = Result.objects.filter(uploaded_by=request.user).select_related('student')
    
    # Get filter parameters
    class_name = request.GET.get('class_name')
    subject = request.GET.get('subject')
    
    if class_name:
        results = results.filter(class_name=class_name)
    if subject:
        results = results.filter(subject__icontains=subject)
    
    # Calculate statistics
    total_students = results.values('student').distinct().count()
    average_marks = results.aggregate(Avg('marks'))['marks__avg'] or 0
    
    context = {
        'results': results,
        'total_students': total_students,
        'average_marks': round(average_marks, 2),
        'class_name': class_name,
        'subject': subject,
        'class_choices': User.CLASS_CHOICES,
    }
    
    return render(request, 'teacher_view_results.html', context)

@login_required
def admin_delete_result(request, result_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can delete results.')
        return redirect('home')
    
    result = get_object_or_404(Result, id=result_id)
    
    if request.method == 'POST':
        student_name = result.student.get_full_name()
        subject = result.subject
        result.delete()
        messages.success(request, f'Result for {student_name} in {subject} deleted successfully!')
        return redirect('admin_manage_results')
    
    return render(request, 'admin_delete_result.html', {'result': result})

@login_required
def upload_study_material(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.subject = request.user.subject  # Auto-fill teacher's subject
            material.save()
            messages.success(request, 'Study material uploaded successfully!')
            return redirect('teacher_dashboard')
    else:
        form = StudyMaterialForm(initial={'subject': request.user.subject})
    
    return render(request, 'upload_study_material.html', {'form': form})

# AJAX view to get students by class
@login_required
def get_students_by_class(request):
    class_name = request.GET.get('class_name')
    students = User.objects.filter(role='student', student_class=class_name, status='approved')
    data = [{'id': s.id, 'name': f'{s.first_name} {s.last_name}', 'roll_number': s.roll_number} for s in students]
    return JsonResponse(data, safe=False)




@login_required
def view_assignments(request):
    if request.user.role != 'student':
        return redirect('home')
    
    assignments = Assignment.objects.filter(class_name=request.user.student_class)
    return render(request, 'view_assignments.html', {'assignments': assignments})


@login_required
def mark_attendance(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    if request.method == 'POST':
        class_name = request.POST.get('class_name')
        date_str = request.POST.get('date')
        
        # Convert string date to actual date object
        try:
            from datetime import datetime
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except:
            messages.error(request, 'Invalid date format')
            return redirect('take_attendance')
        
        # Get all students in the class
        students = User.objects.filter(role='student', student_class=class_name, status='approved')
        
        # Process each student's attendance
        for student in students:
            status_key = f'status_{student.id}'
            if status_key in request.POST:
                status = request.POST[status_key]
                
                # Use update_or_create to handle existing records
                Attendance.objects.update_or_create(
                    student=student,
                    date=attendance_date,  # ✅ Now passing DATE object, not string
                    defaults={
                        'class_name': class_name,
                        'status': status,
                        'marked_by': request.user
                    }
                )
        
        messages.success(request, f'Attendance marked successfully for Class {class_name} on {date_str}')
        return redirect('teacher_dashboard')
    
    return redirect('take_attendance')


@login_required
def admin_view_attendance(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')
    
    # Get filter parameters
    class_name = request.GET.get('class_name', '')
    date_str = request.GET.get('date', '')
    
    attendance_data = None
    summary = None
    
    # If filters are provided
    if class_name and date_str:
        try:
            # Convert date string to date object
            from datetime import datetime
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Get attendance records
            attendance_data = Attendance.objects.filter(
                class_name=class_name,
                date=attendance_date  # ✅ Filter by DATE object, not string
            ).select_related('student', 'marked_by')
            
            # Calculate summary
            if attendance_data.exists():
                total = attendance_data.count()
                present_count = attendance_data.filter(status='present').count()
                absent_count = total - present_count
                attendance_percentage = (present_count / total) * 100 if total > 0 else 0
                
                summary = {
                    'total_students': total,
                    'present_count': present_count,
                    'absent_count': absent_count,
                    'attendance_percentage': round(attendance_percentage, 2)
                }
                
        except ValueError:
            messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
    
    # Get all classes that have attendance records
    classes_with_attendance = Attendance.objects.values_list(
        'class_name', flat=True
    ).distinct().order_by('class_name')
    
    context = {
        'attendance_data': attendance_data,
        'summary': summary,
        'class_name': class_name,
        'selected_date': date_str,
        'classes_with_attendance': classes_with_attendance,
        'class_choices': User.CLASS_CHOICES,
    }
    
    return render(request, 'admin_view_attendance.html', context)


@login_required
def student_view_attendance(request):
    if request.user.role != 'student':
        return redirect('home')
    
    # Get filter parameters
    date_str = request.GET.get('date')
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    # Get attendance records for this student
    attendance_records = Attendance.objects.filter(student=request.user)
    
    # Apply filters
    if date_str:
        try:
            from datetime import datetime
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            attendance_records = attendance_records.filter(date=filter_date)
        except ValueError:
            messages.error(request, 'Invalid date format')
    
    if month:
        attendance_records = attendance_records.filter(date__month=month)
    
    if year:
        attendance_records = attendance_records.filter(date__year=year)
    
    # Calculate statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status='present').count()
    absent_days = total_days - present_days
    attendance_percentage = (present_days / total_days * 100) if total_days > 0 else 0
    
    # Get unique years for filter dropdown
    years = Attendance.objects.filter(student=request.user).dates('date', 'year')
    
    context = {
        'attendance_records': attendance_records.order_by('-date'),
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'attendance_percentage': round(attendance_percentage, 2),
        'date_filter': date_str,
        'month_filter': month,
        'year_filter': year,
        'years': [y.year for y in years],
    }
    
    return render(request, 'student_view_attendance.html', context)




@login_required
def edit_attendance(request, attendance_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can edit attendance.')
        return redirect('home')
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        form = AttendanceEditForm(request.POST, instance=attendance)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('admin_view_attendance')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AttendanceEditForm(instance=attendance)
    
    return render(request, 'edit_attendance.html', {
        'form': form, 
        'attendance': attendance,
        'class_choices': User.CLASS_CHOICES
    })

@login_required
def delete_attendance(request, attendance_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can delete attendance.')
        return redirect('home')
    
    attendance = get_object_or_404(Attendance, id=attendance_id)
    
    if request.method == 'POST':
        student_name = attendance.student.get_full_name
        date = attendance.date
        attendance.delete()
        messages.success(request, f'Attendance record for {student_name} on {date} deleted successfully!')
        return redirect('admin_view_attendance')
    
    return render(request, 'delete_attendance.html', {'attendance': attendance})

@login_required
def teacher_student_performance(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    class_name = request.GET.get('class_name')
    students = User.objects.filter(role='student', status='approved')
    
    if class_name:
        students = students.filter(student_class=class_name)
    
    performance_data = []
    for student in students:
        results = Result.objects.filter(student=student, subject=request.user.subject)
        assignments = Assignment.objects.filter(class_name=student.student_class, subject=request.user.subject)
        attendance = Attendance.objects.filter(student=student, status='present')
        
        performance_data.append({
            'student': student,
            'results': results,
            'assignments_count': assignments.count(),
            'attendance_count': attendance.count(),
            'average_marks': results.aggregate(Avg('marks'))['marks__avg'] or 0
        })
    
    return render(request, 'teacher_student_performance.html', {
        'performance_data': performance_data,
        'selected_class': class_name
    })

@login_required
def admin_analytics(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    # Statistics
    total_students = User.objects.filter(role='student', status='approved').count()
    total_teachers = User.objects.filter(role='teacher', status='approved').count()
    total_assignments = Assignment.objects.count()
    total_results = Result.objects.count()
    
    # Attendance statistics
    attendance_data = Attendance.objects.values('date').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present'))
    ).order_by('-date')[:7]
    
    # Class-wise student count
    class_distribution = User.objects.filter(role='student', status='approved').values(
        'student_class'
    ).annotate(
        count=Count('id')
    ).order_by('student_class')
    
    return render(request, 'admin_analytics.html', {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_assignments': total_assignments,
        'total_results': total_results,
        'attendance_data': attendance_data,
        'class_distribution': class_distribution
    })



def feedback_view(request):
    return render(request, 'feedback.html')

@require_POST
def submit_feedback(request):
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        # In a real application, you might want to add approval process
        feedback.is_approved = True  # Auto-approve for demo purposes
        feedback.save()
        return JsonResponse({'status': 'success', 'message': 'Feedback submitted successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid form data'})

def get_feedback(request):
    # Get approved feedback only
    feedback_list = Feedback.objects.filter(is_approved=True).values(
        'id', 'user_type', 'name', 'email', 'feedback', 'created_at'
    )
    return JsonResponse(list(feedback_list), safe=False)

def careerpage(request):
    if request.method == 'POST':
        form = CareerApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('career')
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = CareerApplicationForm()
    
    return render(request, 'career.html', {'form': form})

@login_required
def admin_career_applications(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('home')
    
    applications = CareerApplication.objects.all().order_by('-applied_at')
    
    return render(request, 'admin_career_applications.html', {
        'applications': applications
    })


@login_required
def delete_application(request, application_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete applications.')
        return redirect('home')
    
    application = get_object_or_404(CareerApplication, id=application_id)
    
    if request.method == 'POST':
        application_name = application.name
        application.delete()
        messages.success(request, f'Application from {application_name} has been deleted successfully!')
        return redirect('admin_career_applications')
    
    return render(request, 'delete_application.html', {'application': application})


@login_required
def admin_notices(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can manage notices.')
        return redirect('home')
    
    notices = Notice.objects.all().order_by('-created_at')
    
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.created_by = request.user
            notice.save()
            messages.success(request, 'Notice created successfully! All teachers and students can now view this notice.')
            return redirect('admin_notices')
    else:
        form = NoticeForm()
    
    return render(request, 'admin_notices.html', {
        'notices': notices,
        'form': form
    })


@login_required
def teacher_notices(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'teacher_notices.html', {'notices': notices})

@login_required
def student_notices(request):
    if request.user.role != 'student':
        return redirect('home')
    
    notices = Notice.objects.all().order_by('-created_at')
    return render(request, 'student_notices.html', {'notices': notices})

@login_required
def view_notice_detail(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)
    return render(request, 'view_notice_detail.html', {'notice': notice})


@login_required
def delete_notice(request, notice_id):
    if not request.user.is_superuser:
        messages.error(request, 'Only admin can delete notices.')
        return redirect('home')
    
    notice = get_object_or_404(Notice, id=notice_id)
    notice.delete()
    messages.success(request, 'Notice deleted successfully.')
    return redirect('admin_notices')



@login_required
def upload_study_material(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can upload study materials.')
        return redirect('home')
    
    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, 'Study material uploaded successfully!')
            return redirect('upload_study_material')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = StudyMaterialForm(initial={'subject': request.user.subject})
    
    # Get teacher's uploaded materials
    teacher_materials = StudyMaterial.objects.filter(uploaded_by=request.user).order_by('-uploaded_at')
    
    return render(request, 'upload_study_material.html', {
        'form': form,
        'teacher_materials': teacher_materials
    })

@login_required
def view_study_materials(request):
    if request.user.role != 'student':
        messages.error(request, 'Only students can view study materials.')
        return redirect('home')
    
    # Get materials for student's class
    materials = StudyMaterial.objects.filter(class_name=request.user.student_class).order_by('-uploaded_at')
    
    return render(request, 'view_study_materials.html', {
        'materials': materials,
        'student_class': request.user.student_class
    })

@login_required
def delete_study_material(request, material_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Only teachers can delete study materials.')
        return redirect('home')
    
    material = get_object_or_404(StudyMaterial, id=material_id)
    
    # Check if the teacher owns this material
    if material.uploaded_by != request.user:
        messages.error(request, 'You can only delete your own study materials.')
        return redirect('upload_study_material')
    
    if request.method == 'POST':
        material_title = material.title
        material.file.delete()  # Delete the file from storage
        material.delete()       # Delete the database record
        messages.success(request, f'Study material "{material_title}" deleted successfully!')
        return redirect('upload_study_material')
    
    return render(request, 'delete_study_material.html', {'material': material})


@login_required
def submit_assignment(request, assignment_id):
    if request.user.role != 'student':
        return redirect('home')
    
    assignment = get_object_or_404(Assignment, id=assignment_id)
    
    # Check if already submitted
    try:
        submission = AssignmentSubmission.objects.get(assignment=assignment, student=request.user)
        is_submitted = True
    except AssignmentSubmission.DoesNotExist:
        submission = None
        is_submitted = False
    
    if request.method == 'POST':
        form = AssignmentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
        # If already submitted, update the submission
            if is_submitted:
                submission.submitted_file = form.cleaned_data['submitted_file']
                submission.submission_date = timezone.now()
            # Check if the assignment has a due date before checking lateness
                if submission.assignment.due_date:
                    submission.status = 'late' if submission.is_late() else 'submitted'
                else:
                    submission.status = 'submitted'
                submission.save()
                messages.success(request, 'Assignment resubmitted successfully!')
            else:
            # Create new submission
                submission = form.save(commit=False)
                submission.assignment = assignment
                submission.student = request.user
                submission.submission_date = timezone.now()
            # Check if the assignment has a due date before checking lateness
                if submission.assignment.due_date:
                    submission.status = 'late' if submission.is_late() else 'submitted'
                else:
                    submission.status = 'submitted'
                submission.save()
                messages.success(request, 'Assignment submitted successfully!')
        
            return redirect('view_assignments')
    else:
        form = AssignmentSubmissionForm()
    
    context = {
        'assignment': assignment,
        'form': form,
        'is_submitted': is_submitted,
        'submission': submission
    }
    return render(request, 'submit_assignment.html', context)
@login_required
def view_all_submissions(request,assignment_id):
    if request.user.role != 'teacher':
        return redirect('home')
    
    # Get all assignments created by this teacher
    teacher_assignments = Assignment.objects.filter(created_by=request.user)
    
    # Get filter parameters
    class_name = request.GET.get('class_name', '')
    assignment_id = request.GET.get('assignment', '')
    status_filter = request.GET.get('status', '')
    
    # Start with all submissions for this teacher's assignments
    submissions = AssignmentSubmission.objects.filter(
        assignment__in=teacher_assignments
    ).select_related('student', 'assignment')
    
    # Apply filters
    if class_name:
        submissions = submissions.filter(assignment__class_name=class_name)
    
    if assignment_id:
        submissions = submissions.filter(assignment_id=assignment_id)
    
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    # Get unique classes from the teacher's assignments for the filter dropdown
    class_list = teacher_assignments.values_list('class_name', flat=True).distinct()
    
    context = {
        'submissions': submissions.order_by('-submission_date'),
        'teacher_assignments': teacher_assignments,
        'class_list': class_list,
        'selected_class': class_name,
        'selected_assignment': assignment_id,
        'selected_status': status_filter,
        'status_choices': [('', 'All Status'), ('submitted', 'Submitted'), ('graded', 'Graded'), ('late', 'Late')]
    }
    
    return render(request, 'view_all_submissions.html', context)


@login_required
def grade_submission(request, submission_id):
    if request.user.role != 'teacher':
        return redirect('home')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    # Ensure the teacher owns this assignment
    if submission.assignment.created_by != request.user:
        messages.error(request, 'You are not authorized to grade this assignment.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = GradeAssignmentForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment graded successfully for {submission.student.get_full_name()}')
            return redirect('view_submissions', assignment_id=submission.assignment.id)
    else:
        form = GradeAssignmentForm(instance=submission)
    
    context = {
        'submission': submission,
        'form': form
    }
    return render(request, 'grade_submission.html', context)


@login_required
def admin_manage_fees(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    fee_structures = FeeStructure.objects.all()
    fee_payments = FeePayment.objects.all().select_related('student', 'fee_structure')
    
    # Get filter parameters
    class_name = request.GET.get('class_name', '')
    status = request.GET.get('status', '')
    
    if class_name:
        fee_payments = fee_payments.filter(fee_structure__class_name=class_name)
    
    if status:
        fee_payments = fee_payments.filter(status=status)
    
    # Calculate statistics
    total_collected = fee_payments.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    pending_amount = fee_payments.filter(status='pending').aggregate(Sum('fee_structure__amount'))['fee_structure__amount__sum'] or 0
    
    context = {
        'fee_structures': fee_structures,
        'fee_payments': fee_payments.order_by('-payment_date'),
        'total_collected': total_collected,
        'pending_amount': pending_amount,
        'selected_class': class_name,
        'selected_status': status,
        'class_choices': User.CLASS_CHOICES,
    }
    
    return render(request, 'admin_manage_fees.html', context)

@login_required
def add_fee_structure(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee structure added successfully!')
            return redirect('admin_manage_fees')
    else:
        form = FeeStructureForm()
    
    return render(request, 'add_fee_structure.html', {'form': form})

@login_required
def record_fee_payment(request):
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == 'POST':
        form = FeePaymentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fee payment recorded successfully!')
            return redirect('admin_manage_fees')
    else:
        form = FeePaymentForm()
    
    return render(request, 'record_fee_payment.html', {'form': form})

@login_required
def student_view_fees(request):
    if request.user.role != 'student':
        return redirect('home')
    
    # Get fee payments for this student
    fee_payments = FeePayment.objects.filter(student=request.user)
    
    # Get filter parameters
    month = request.GET.get('month')
    year = request.GET.get('year')
    
    if month:
        fee_payments = fee_payments.filter(payment_date__month=month)
    
    if year:
        fee_payments = fee_payments.filter(payment_date__year=year)
    
    # Calculate statistics
    total_paid = fee_payments.filter(status='paid').aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    pending_payments = fee_payments.filter(status='pending')
    total_pending = sum(payment.fee_structure.amount for payment in pending_payments)
    
    context = {
        'fee_payments': fee_payments.order_by('-payment_date'),
        'total_paid': total_paid,
        'total_pending': total_pending,
        'pending_payments': pending_payments,
        'month_filter': month,
        'year_filter': year,
    }
    
    return render(request, 'student_view_fees.html', context)


@login_required
def view_submissions(request, assignment_id):
    if request.user.role != 'teacher':
        return redirect('home')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    # Calculate statistics
    total_submissions = submissions.count()
    graded_count = submissions.filter(status='graded').count()
    pending_count = submissions.filter(status='submitted').count()
    late_count = submissions.filter(status='late').count()
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'total_submissions': total_submissions,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'late_count': late_count,
    }
    
    return render(request, 'view_submissions.html', context)

@login_required
def grade_submission(request, submission_id):
    if request.user.role != 'teacher':
        return redirect('home')
    
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    # Ensure the teacher owns this assignment
    if submission.assignment.created_by != request.user:
        messages.error(request, 'You are not authorized to grade this assignment.')
        return redirect('teacher_dashboard')
    
    if request.method == 'POST':
        form = GradeAssignmentForm(request.POST, instance=submission)
        if form.is_valid():
            form.save()
            messages.success(request, f'Assignment graded successfully for {submission.student.get_full_name()}')
            return redirect('view_submissions', assignment_id=submission.assignment.id)
    else:
        form = GradeAssignmentForm(instance=submission)
    
    context = {
        'submission': submission,
        'form': form
    }
    return render(request, 'grade_submission.html', context)

@login_required
def view_all_submissions(request):
    if request.user.role != 'teacher':
        return redirect('home')
    
    # Get all assignments created by this teacher
    teacher_assignments = Assignment.objects.filter(created_by=request.user)
    
    # Get all submissions for these assignments
    submissions = AssignmentSubmission.objects.filter(
        assignment__in=teacher_assignments
    ).select_related('student', 'assignment').order_by('-submission_date')
    
    # Get filter parameters
    class_name = request.GET.get('class_name', '')
    assignment_id = request.GET.get('assignment', '')
    status_filter = request.GET.get('status', '')
    
    # Apply filters
    if class_name:
        submissions = submissions.filter(assignment__class_name=class_name)
    
    if assignment_id:
        submissions = submissions.filter(assignment_id=assignment_id)
    
    if status_filter:
        submissions = submissions.filter(status=status_filter)
    
    # Get unique classes from the teacher's assignments for the filter dropdown
    class_list = teacher_assignments.values_list('class_name', flat=True).distinct()
    
    context = {
        'submissions': submissions,
        'teacher_assignments': teacher_assignments,
        'class_list': class_list,
        'selected_class': class_name,
        'selected_assignment': assignment_id,
        'selected_status': status_filter,
        'status_choices': [('', 'All Status'), ('submitted', 'Submitted'), ('graded', 'Graded'), ('late', 'Late')]
    }
    
    return render(request, 'view_all_submissions.html', context)

@login_required
def view_assignment_submissions(request, assignment_id):
    if request.user.role != 'teacher':
        return redirect('home')
    
    assignment = get_object_or_404(Assignment, id=assignment_id, created_by=request.user)
    submissions = AssignmentSubmission.objects.filter(assignment=assignment).select_related('student')
    
    # Calculate statistics
    total_submissions = submissions.count()
    graded_count = submissions.filter(status='graded').count()
    pending_count = submissions.filter(status='submitted').count()
    late_count = submissions.filter(status='late').count()
    
    context = {
        'assignment': assignment,
        'submissions': submissions,
        'total_submissions': total_submissions,
        'graded_count': graded_count,
        'pending_count': pending_count,
        'late_count': late_count,
    }
    
    return render(request, 'view_assignment_submissions.html', context)