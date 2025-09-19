from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User,Assignment,Result,StudyMaterial,Attendance,Notice,Feedback,CareerApplication,AssignmentSubmission,FeeStructure,FeePayment
from django.utils import timezone
from django.core.validators import validate_email
from datetime import date
# Add class choices
CLASS_CHOICES = [
    ('', 'Select Class'),
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
class StudentRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, validators=[validate_email])
    student_class = forms.ChoiceField(choices=CLASS_CHOICES[1:], required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'student_class', 'username', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class TeacherRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True, validators=[validate_email])
    qualification = forms.CharField(max_length=100, required=True)
    subject = forms.CharField(max_length=50, required=True)
    

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'qualification', 'subject', 'username', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class TeacherEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'qualification', 'subject', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'student_class', 'username']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'student_class': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email address is already registered.")
        return email


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['class_name', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'class_name': forms.Select(attrs={'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default date to today
        self.fields['date'].initial = timezone.now().date()

class StudentAttendanceForm(forms.Form):
    def __init__(self, *args, **kwargs):
        students = kwargs.pop('students')
        super().__init__(*args, **kwargs)
        for student in students:
            self.fields[f'status_{student.id}'] = forms.ChoiceField(
                choices=[('present', 'Present'), ('absent', 'Absent')],
                initial='present',
                widget=forms.Select(attrs={'class': 'form-control'})
            )


class StudentAttendanceFilterForm(forms.Form):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    month = forms.ChoiceField(
        choices=[('', 'All Months')] + [
            ('1', 'January'), ('2', 'February'), ('3', 'March'),
            ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'})
    )

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'class_name', 'subject', 'due_date', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if not due_date:
            raise forms.ValidationError("Due date is required.")
        return due_date


class ResultFilterForm(forms.Form):
    class_name = forms.ChoiceField(
        choices=[('', 'All Classes')] + list(User.CLASS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    subject = forms.ChoiceField(
        choices=[],  # Will be populated in view
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = ['student', 'class_name', 'subject', 'marks', 'total_marks']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit students to approved ones only
        self.fields['student'].queryset = User.objects.filter(role='student', status='approved')



class AttendanceEditForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'class_name', 'status', 'marked_by']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'marked_by': forms.Select(attrs={'class': 'form-control'}),
        }



class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['user_type', 'name', 'email', 'feedback']
        widgets = {
            'user_type': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Please share your thoughts...'}),
        }

class CareerApplicationForm(forms.ModelForm):
    class Meta:
        model = CareerApplication
        fields = ['name', 'age', 'place', 'qualification', 'resume', 'contact']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 18, 'required': True}),
            'place': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'qualification': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'pattern': '[0-9]{10}', 'required': True}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resume'].widget.attrs.update({
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx',
            'required': True
        })

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content', 'is_important']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter notice title',
                'required': True
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Enter notice content...',
                'required': True
            }),
            'is_important': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_important'].required = False


class StudyMaterialForm(forms.ModelForm):
    class Meta:
        model = StudyMaterial
        fields = ['title', 'description', 'class_name', 'subject', 'file']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter material title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter description...',
                'required': True
            }),
            'class_name': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.mp4,.mp3',
            'required': True
        })


class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_file']
        widgets = {
            'submitted_file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.txt,.zip,.rar',
                'required': True
            })
        }

class GradeAssignmentForm(forms.ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['marks_obtained', 'feedback', 'status']
        widgets = {
            'marks_obtained': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Enter feedback for the student...'
            }),
            'status': forms.Select(attrs={'class': 'form-control'})
        }


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure
        fields = ['class_name', 'amount', 'academic_year', 'is_active']
        widgets = {
            'class_name': forms.Select(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'academic_year': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2023-2024'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment
        fields = ['student', 'fee_structure', 'amount_paid', 'payment_date', 'due_date', 'status', 'transaction_id', 'payment_method']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'fee_structure': forms.Select(attrs={'class': 'form-control'}),
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit students to approved ones only
        self.fields['student'].queryset = User.objects.filter(role='student', status='approved')

class StudentFeeFilterForm(forms.Form):
    month = forms.ChoiceField(
        choices=[('', 'All Months')] + [
            ('1', 'January'), ('2', 'February'), ('3', 'March'),
            ('4', 'April'), ('5', 'May'), ('6', 'June'),
            ('7', 'July'), ('8', 'August'), ('9', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Year'})
    )