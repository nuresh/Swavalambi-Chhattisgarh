from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django.core.exceptions import ValidationError

def validate_file_size(file):
    max_size_kb = 2024  # Maximum file size in KB (e.g., 50 MB)
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"File size should not exceed {max_size_kb} KB.") 

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False)  
    
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100,null=True, blank=True)
    branch_name = models.CharField(max_length=100,null=True, blank=True)
    semester = models.IntegerField(default=1,null=True, blank=True)
    enrollment_number = models.CharField(max_length=30,null=True, blank=True)
    roll_number = models.CharField(max_length=30,null=True, blank=True)
    gender = models.CharField(max_length=30,null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    course_starting_year = models.IntegerField(null=True, blank=True)
    course_ending_year = models.IntegerField(null=True, blank=True)
    profile_tagline = models.CharField(max_length=1000,null=True, blank=True)
    profile_summary = models.CharField(max_length=1000,null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    skills = models.CharField(max_length=1000,null=True, blank=True)
    resume = models.CharField(max_length=1000,null=True, blank=True)
    linkedin = models.CharField(max_length=1000,null=True, blank=True)
    github = models.CharField(max_length=1000,null=True, blank=True)
    website = models.CharField(max_length=1000,null=True, blank=True)
    phone_number = models.CharField(max_length=10,null=True, blank=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    head_of_department = models.CharField(max_length=100,null=True, blank=True)

    def __str__(self):
        return self.department_name


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    address = models.TextField(null=True, blank=True)
    gst = models.CharField(max_length=15,null=True, blank=True)
    industry_name = models.CharField(max_length=40,null=True, blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    AutoSlugField(populate_from='name', unique=True,null=True,default=None)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    qty =  models.IntegerField(null=True, blank=True)
    desc = models.CharField(max_length=500,null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    image = models.FileField(upload_to="product_image",max_length=250, null=True, default=None,validators=[validate_file_size])
    enabled = models.BooleanField(default=True,null=True)
    is_approved = models.BooleanField(default=False,null=True)
    is_rejected = models.BooleanField(default=False,null=True)


    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    AutoSlugField(populate_from='name', unique=True,null=True,default=None)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    duration = models.CharField(max_length=100,null=True, blank=True)
    desc = models.CharField(max_length=500,null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    # image = models.FileField(upload_to="product_image",max_length=250, null=True, default=None,validators=[validate_file_size])
    enabled = models.BooleanField(default=True,null=True)
    is_approved = models.BooleanField(default=False,null=True)
    is_rejected = models.BooleanField(default=False,null=True)


    def __str__(self):
        return self.name


# class job(models.Model):
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     company_name = models.ForeignKey(Company, on_delete=models.CASCADE,blank=True,null=True)
#     job_title = models.CharField(max_length=200)
#     job_description = models.TextField()
#     job_location = models.CharField(max_length=200)
#     job_type = models.CharField(max_length=200,choices=TYPE_CHOICES)
#     job_experience = models.CharField(max_length=200,choices=EXPERIENCE_CHOICES)
#     job_salary = models.CharField(max_length=200)
#     job_skills = models.ForeignKey(skills, on_delete=models.CASCADE,blank=True,null=True)
#     job_role = models.CharField(max_length=200,choices=JOB_ROLE_CHOICES)
#     job_posted_on = models.DateField(auto_now_add=True)
#     job_last_date = models.DateField()
#     job_posted_by = models.CharField(max_length=200)
#     contact_email = models.EmailField()
#     active = models.BooleanField(default=True)
#     timing = models.CharField(max_length=30,choices=TIMING_CHOICES)

#     def __str__(self):
#         return self.job_title

#     class Meta:
#         verbose_name_plural = "Jobs"

# class applications(models.Model):
#     user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
#     student = models.ForeignKey(Student, on_delete=models.CASCADE)
#     job = models.ForeignKey(job, on_delete=models.CASCADE)
#     switch = models.BooleanField(default=True)
#     application_status = models.CharField(max_length=200,default="Applied")

#     def __str__(self):
#         return self.job.job_title
    
#     class Meta:
#         verbose_name_plural = "Applications"
