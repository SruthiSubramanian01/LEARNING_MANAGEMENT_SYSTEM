from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Static pages
    path('', views.homepage, name='home'),
    path('about/', views.aboutpage, name='about'),
    path('courses/', views.coursespage, name='courses'),
    path('contact/', views.contactpage, name='contact'),
    path('gallery/', views.gallerypage, name='gallery'),
    path('team/', views.teampage, name='team'),

    # Career URLs
    path('career/', views.careerpage, name='career'),
    path('admin-career-applications/', views.admin_career_applications, name='admin_career_applications'),
    path('admin-delete-application/<int:application_id>/', views.delete_application, name='delete_application'),

    # Feedback URLs
    path('feedback/', views.feedback_view, name='feedback'),
    path('submit-feedback/', views.submit_feedback, name='submit_feedback'),
    path('get-feedback/', views.get_feedback, name='get_feedback'),

    # Authentication URLs
    path('register/student/', views.student_register, name='student_register'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),

    # Dashboard URLs
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher-dashboard/', views.teacher_dashboard, name='teacher_dashboard'),

    # User approval URLs
    path('approve-user/<int:user_id>/', views.approve_user, name='approve_user'),
    path('reject-user/<int:user_id>/', views.reject_user, name='reject_user'),
    path('pending-requests/', views.pending_requests, name='pending_requests'),
    path('pending-approval/', views.pending_approval, name='pending_approval'),

    # Admin management URLs
    path('admin-manage-teachers/', views.manage_teachers, name='manage_teachers'),
    path('admin-edit-teacher/<int:teacher_id>/', views.edit_teacher, name='edit_teacher'),
    path('admin-delete-teacher/<int:teacher_id>/', views.delete_teacher, name='delete_teacher'),
    path('admin-manage-students/', views.manage_students, name='manage_students'),
    path('admin-edit-student/<int:student_id>/', views.edit_student, name='edit_student'),
    path('admin-delete-student/<int:student_id>/', views.delete_student, name='delete_student'),
    path('admin-manage-results/', views.admin_manage_results, name='admin_manage_results'),
    path('admin-delete-result/<int:result_id>/', views.admin_delete_result, name='admin_delete_result'),
    path('admin-view-attendance/', views.admin_view_attendance, name='admin_view_attendance'),
    path('admin-edit-attendance/<int:attendance_id>/', views.edit_attendance, name='edit_attendance'),
    path('admin-delete-attendance/<int:attendance_id>/', views.delete_attendance, name='delete_attendance'),
    path('admin-analytics/', views.admin_analytics, name='admin_analytics'),
    

    # Teacher URLs
    path('teacher-take-attendance/', views.take_attendance, name='take_attendance'),
    path('teacher-mark-attendance/', views.mark_attendance, name='mark_attendance'),
    path('teacher-upload-assignment/', views.upload_assignment, name='upload_assignment'),
    path('teacher-upload-marks/', views.upload_marks, name='upload_marks'),
    path('teacher-view-results/', views.teacher_view_results, name='teacher_view_results'),
    path('teacher-student-performance/', views.teacher_student_performance, name='teacher_student_performance'),
    

    # Student URLs
    path('student-view-assignments/', views.view_assignments, name='view_assignments'),
    
    path('student-view-results/', views.student_view_results, name='student_view_results'),
    path('student-view-attendance/', views.student_view_attendance, name='student_view_attendance'),

    # AJAX URLs
    path('ajax/get-students-by-class/', views.get_students_by_class, name='get_students_by_class'),

    # Notice URLs
    path('admin-notices/', views.admin_notices, name='admin_notices'),
    path('notice/<int:notice_id>/', views.view_notice_detail, name='view_notice_detail'),
    path('admin-delete-notice/<int:notice_id>/', views.delete_notice, name='delete_notice'),
    path('teacher/notices/', views.teacher_notices, name='teacher_notices'),
    path('student/notices/', views.student_notices, name='student_notices'),

    # Study Material URLs
    path('teacher/upload-study-material/', views.upload_study_material, name='upload_study_material'),
    path('student/view-study-materials/', views.view_study_materials, name='view_study_materials'),
    path('teacher/delete-study-material/<int:material_id>/', views.delete_study_material, name='delete_study_material'),


    path('test-email/', views.test_email_setup, name='test_email'), 

        # Add these to your urlpatterns list
    path('assignment/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignment/<int:assignment_id>/submissions/', views.view_all_submissions, name='view_all_submissions'),
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('submissions/', views.view_all_submissions, name='view_all_submissions'),
    path('assignment/<int:assignment_id>/submissions/', views.view_assignment_submissions, name='view_assignment_submissions'), 

        # Fee Management URLs
    path('admin-manage-fees/', views.admin_manage_fees, name='admin_manage_fees'),
    path('admin-add-fee-structure/', views.add_fee_structure, name='add_fee_structure'),
    path('admin-record-fee-payment/', views.record_fee_payment, name='record_fee_payment'),
    path('student-view-fees/', views.student_view_fees, name='student_view_fees'),


]

# This is IMPORTANT for serving uploaded files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)