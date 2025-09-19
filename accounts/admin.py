from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,Attendance,Assignment,Result,Notice,StudyMaterial,Feedback,CareerApplication,FeePayment,FeeStructure
from django.utils import timezone
from django.utils.html import format_html


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'status', 'student_class', 'is_staff')
    list_filter = ('role', 'status', 'student_class', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'status', 'student_class', 'qualification', 'subject')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('role', 'status', 'student_class', 'qualification', 'subject')}),
    )
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'class_name', 'status', 'marked_by', 'created_at')
    list_filter = ('class_name', 'status', 'date', 'marked_by')
    search_fields = ('student__username', 'student__first_name', 'student__last_name')
    readonly_fields = ('created_at',)
    
    # Add this to make it easier to view attendance in admin
    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('student', 'date', 'class_name', 'status', 'marked_by', 'created_at')
        else:
            return ('student', 'date', 'class_name', 'status', 'created_at')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_name', 'subject', 'due_date', 'created_by')
    list_filter = ('class_name', 'subject', 'due_date')
    search_fields = ('title', 'subject')


@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_name', 'subject', 'marks', 'total_marks', 'percentage', 'grade', 'uploaded_by', 'uploaded_at')
    list_filter = ('class_name', 'subject', 'uploaded_by')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'subject')
    readonly_fields = ('uploaded_at',)
    
    def percentage(self, obj):
        return f"{obj.percentage():.2f}%"
    percentage.short_description = 'Percentage'
    
    def grade(self, obj):
        return obj.grade()
    grade.short_description = 'Grade'



@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'created_at')
    search_fields = ('title', 'content')

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_name', 'subject', 'uploaded_by', 'uploaded_at')
    list_filter = ('class_name', 'subject')
    search_fields = ('title', 'subject')



@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user_type', 'name', 'email', 'created_at', 'is_approved')
    list_filter = ('user_type', 'is_approved', 'created_at')
    search_fields = ('name', 'email', 'feedback')
    list_editable = ('is_approved',)
    actions = ['approve_feedback']
    
    def approve_feedback(self, request, queryset):
        queryset.update(is_approved=True)
    approve_feedback.short_description = "Approve selected feedback"


@admin.register(CareerApplication)
class CareerApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'age', 'place', 'qualification', 'contact', 'applied_at', 'view_resume_link')
    list_filter = ('qualification', 'applied_at')
    search_fields = ('name', 'place', 'contact')
    readonly_fields = ('applied_at',)
    
    def view_resume_link(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">📄 View Resume</a>', obj.resume.url)
        return "No resume"
    view_resume_link.short_description = 'Resume'


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('class_name', 'amount', 'academic_year', 'is_active')
    list_filter = ('class_name', 'academic_year', 'is_active')
    search_fields = ('class_name', 'academic_year')
    list_editable = ('is_active',)

@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'fee_structure', 'amount_paid', 'payment_date', 'due_date', 'status')
    list_filter = ('status', 'payment_date', 'payment_method')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'transaction_id')
    readonly_fields = ('created_at',)

