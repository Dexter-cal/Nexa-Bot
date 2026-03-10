from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=[
        ('superadmin', 'Super Admin'),
        ('admin', 'Admin'),
        ('bursar', 'Bursar'),
        ('reception', 'Reception'),
        ('teacher', 'Teacher'),
        ('parent', 'Parent'),
        ('student', 'Student'),
    ])
    avatar = models.CharField(max_length=2, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    must_change_password = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class SchoolSettings(models.Model):
    mtn_api_key = models.CharField(max_length=255, blank=True, null=True)
    airtel_api_key = models.CharField(max_length=255, blank=True, null=True)
    school_account_number = models.CharField(max_length=50, blank=True, null=True)
    current_term = models.IntegerField(default=2)
    current_year = models.IntegerField(default=2025)

    class Meta:
        verbose_name_plural = "School Settings"

class SchoolClass(models.Model):
    level = models.CharField(max_length=20)
    sections = models.JSONField(default=list)
    annual_fee = models.DecimalField(max_digits=12, decimal_places=2)
    max_students_per_section = models.IntegerField(default=40)
    teacher_a = models.CharField(max_length=100, blank=True, null=True)
    teacher_b = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Class {self.level}"

class Teacher(models.Model):
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='teacher_info', null=True, blank=True)
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    subjects = models.JSONField(default=list)
    assigned_class = models.CharField(max_length=100, blank=True, null=True)
    employment_type = models.CharField(max_length=50, default='Permanent')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    student_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10)
    district = models.CharField(max_length=100, blank=True, null=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    current_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True)
    section = models.CharField(max_length=10)
    enrollment_date = models.DateField(auto_now_add=True)
    parent_name = models.CharField(max_length=100)
    parent_relationship = models.CharField(max_length=50)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Active')
    photo = models.ImageField(upload_to='student_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.student_id})"

class FeeStructure(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    term = models.IntegerField()
    year = models.IntegerField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)

class Timetable(models.Model):
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE)
    section = models.CharField(max_length=10)
    slots = models.JSONField(default=list)
    cells = models.JSONField(default=dict)

class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    score = models.IntegerField()
    term = models.IntegerField()
    year = models.IntegerField()
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=10) # Present, Absent, Late
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
