from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import os
from django.core.validators import validate_email
# Create your models here.

class User(AbstractUser):
    ROLE_CHOICES = (
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    # Add choices for student_class
    CLASS_CHOICES = [
        ('1', 'Class 1'),
        ('2', 'Class 2'),
        ('3', 'Class 3'),
        ('4', 'Class 4'),
        ('5', 'Class 5'),
        ('6', 'Class 6'),
        ('7', 'Class 7'),
        ('8', 'Class 8'),
        ('9', 'Class 9'),
        ('10', 'Class 10'),
        ('11', 'Class 11'),
        ('12', 'Class 12'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    student_class = models.CharField(max_length=20, blank=True, null=True)
    qualification = models.CharField(max_length=100, blank=True, null=True)
    subject = models.CharField(max_length=50, blank=True, null=True)
    
    email = models.EmailField(unique=True, validators=[validate_email])

    def __str__(self):
        return f"{self.username} ({self.role})"

class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    date = models.DateField(default=timezone.now)
    class_name = models.CharField(max_length=20, choices=User.CLASS_CHOICES)
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])
    marked_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marked_attendances', limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'date']
    
    def __str__(self):
        return f"{self.student.username} - {self.date} - {self.status}"

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    class_name = models.CharField(max_length=20, choices=User.CLASS_CHOICES)
    subject = models.CharField(max_length=50)
    due_date = models.DateTimeField()  # Remove null=True, blank=True if they exist
    file = models.FileField(upload_to='assignments/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class Result(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    class_name = models.CharField(max_length=20, choices=User.CLASS_CHOICES)
    subject = models.CharField(max_length=50)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_results', limit_choices_to={'role': 'teacher'})
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.username} - {self.subject} - {self.marks}"
    
    def percentage(self):
        return (self.marks / self.total_marks) * 100
    
    def grade(self):
        percentage = self.percentage()
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C+'
        elif percentage >= 40:
            return 'C'
        else:
            return 'F'






class Feedback(models.Model):
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('public', 'Public'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    feedback = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.get_user_type_display()} Feedback - {self.created_at.strftime('%Y-%m-%d')}"
    
    class Meta:
        ordering = ['-created_at']

class CareerApplication(models.Model):
    QUALIFICATION_CHOICES = [
        ('high_school', 'High School'),
        ('diploma', 'Diploma'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    place = models.CharField(max_length=100)
    qualification = models.CharField(max_length=20, choices=QUALIFICATION_CHOICES)
    resume = models.FileField(upload_to='career_resumes/')
    contact = models.CharField(max_length=15)
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_qualification_display()}"
    
    def filename(self):
        return os.path.basename(self.resume.name)
    
class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['admin', 'teacher']})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_important = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def short_content(self):
        return self.content[:100] + '...' if len(self.content) > 100 else self.content
    
class StudyMaterial(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    class_name = models.CharField(max_length=20, choices=User.CLASS_CHOICES)
    subject = models.CharField(max_length=50)
    file = models.FileField(upload_to='study_materials/')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def file_extension(self):
        return os.path.splitext(self.file.name)[1].lower()
    
    def file_icon(self):
        extension = self.file_extension()
        if extension in ['.pdf']:
            return '📄'
        elif extension in ['.doc', '.docx']:
            return '📝'
        elif extension in ['.ppt', '.pptx']:
            return '📊'
        elif extension in ['.xls', '.xlsx']:
            return '📈'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
            return '🖼️'
        elif extension in ['.mp4', '.avi', '.mov']:
            return '🎥'
        elif extension in ['.mp3', '.wav']:
            return '🎵'
        else:
            return '📁'


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    submitted_file = models.FileField(upload_to='assignment_submissions/')
    submission_date = models.DateTimeField(auto_now_add=True)
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('late', 'Late Submission')
    ], default='submitted')
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submission_date']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"
    def is_late(self):
    # Check if both dates are available
        if not self.submission_date or not self.assignment.due_date:
         return False
        return self.submission_date > self.assignment.due_date


class FeeStructure(models.Model):
    class_name = models.CharField(max_length=20, choices=User.CLASS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    academic_year = models.CharField(max_length=9, default=f"{timezone.now().year}-{timezone.now().year+1}")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['class_name', 'academic_year']
    
    def __str__(self):
        return f"Class {self.class_name} - ₹{self.amount} ({self.academic_year})"

class FeePayment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
    )
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    payment_method = models.CharField(max_length=50, default='Cash', choices=[('cash', 'Cash'), ('online', 'Online')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.student.username} - ₹{self.amount_paid} - {self.payment_date}"
    
    def is_overdue(self):
        return timezone.now().date() > self.due_date and self.status != 'paid'
    
    def save(self, *args, **kwargs):
        # Update status based on due date
        if self.is_overdue():
            self.status = 'overdue'
        super().save(*args, **kwargs)