from django.db import models
from django.contrib.auth.models import User

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)  
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100)
    branch_name = models.CharField(max_length=100)
    semester = models.IntegerField(default=1)
    enrollment_number = models.CharField(max_length=30)
    roll_number = models.CharField(max_length=30)
    gender = models.CharField(max_length=30)
    date_of_birth = models.DateField(null=True)
    course_starting_year = models.IntegerField()
    course_ending_year = models.IntegerField()
    profile_tagline = models.CharField(max_length=1000,blank=True)
    profile_summary = models.CharField(max_length=1000,blank=True)
    experience = models.IntegerField(blank=False)
    skills = models.CharField(max_length=1000)
    resume = models.CharField(max_length=1000)
    linkedin = models.CharField(max_length=1000,blank=True)
    github = models.CharField(max_length=1000,blank=True)
    website = models.CharField(max_length=1000,blank=True)
    phone_number = models.CharField(max_length=10)

    def __str__(self):
        return self.name


class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100)

    def __str__(self):
        return self.department_name


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    address = models.TextField()
    gst = models.CharField(max_length=15)
    industry_name = models.CharField(max_length=40)

    def __str__(self):
        return self.name