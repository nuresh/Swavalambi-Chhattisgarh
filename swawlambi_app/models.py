from django.db import models
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from django.core.exceptions import ValidationError
from django.utils.text import slugify
import os

def validate_file_size(file):
    max_size_kb = 2024  # Maximum file size in KB (e.g., 50 MB)
    if file.size > max_size_kb * 1024:
        raise ValidationError(f"File size should not exceed {max_size_kb} KB.") 


def notice_file_upload_path(instance, filename):
    if instance.type:
        # Generate dynamic upload path based on the type's name
        upload_to = f"notices/{slugify(instance.type.name)}"
        return os.path.join(upload_to, filename)
    else:
        return "notices/" + filename  # Default path if type is not set

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_super_admin = models.BooleanField(default=False) 


class Admin_Details(models.Model):
    name = models.CharField(max_length=100)
    mobile = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    course_name = models.CharField(max_length=100,null=True, blank=True)
    branch_name = models.CharField(max_length=100,null=True, blank=True)
    semester = models.IntegerField(null=True, blank=True)
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
    phone_number = models.IntegerField()

    def __str__(self):
        return self.name

    def clean_none_fields(self):
        """Convert None values to empty strings before saving."""
        for field in self._meta.fields:
            if isinstance(field, models.CharField):
                value = getattr(self, field.name)
                if value is None:
                    setattr(self, field.name, '')  # Convert None to empty string

    def save(self, *args, **kwargs):
        self.clean_none_fields()  # Ensure all CharFields are not None
        super().save(*args, **kwargs)

class Department(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department_name = models.CharField(max_length=100)
    concerened_person = models.CharField(max_length=100,null=True, blank=True)
    head_of_department = models.CharField(max_length=100,null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.department_name


class Recruiter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    hr_name = models.CharField(max_length=100,null=True, blank=True)
    hr_mail = models.CharField(max_length=100,null=True, blank=True)
    hr_mobile = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200,null=True, blank=True)
    gst = models.CharField(max_length=15,null=True, blank=True)
    industry_type = models.CharField(max_length=40,null=True, blank=True)
    company_phone_number = models.IntegerField(null=True, blank=True)
    first_login = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def clean_none_fields(self):
        """Convert None values to empty strings for CharFields, and handle IntegerFields properly."""
        for field in self._meta.fields:
            value = getattr(self, field.name)

            if isinstance(field, models.CharField) or isinstance(field, models.TextField):
                if value is None:
                    setattr(self, field.name, '')
            elif isinstance(field, models.IntegerField):
                if value is None:
                    setattr(self, field.name, 0)  # Or keep it as None based on preference

    def save(self, *args, **kwargs):
        self.clean_none_fields()  # Ensure all CharFields are not None
        super().save(*args, **kwargs)
            


class Product(models.Model):
    name = models.CharField(max_length=100)
    AutoSlugField(populate_from='name', unique=True,null=True,default=None)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    qty =  models.IntegerField(null=True, blank=True)
    desc = models.CharField(max_length=500,null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    image = models.FileField(upload_to="product_image",max_length=250, null=True, default=None,validators=[validate_file_size])
    amazon_link = models.CharField(max_length=1000,null=True, blank=True)
    flipkart_link = models.CharField(max_length=1000,null=True, blank=True)
    enabled = models.BooleanField(default=True,null=True)
    # is_approved = models.BooleanField(default=False,null=True)
    # is_rejected = models.BooleanField(default=False,null=True)
    

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100)
    AutoSlugField(populate_from='name', unique=True,null=True,default=None)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    duration = models.CharField(max_length=100,null=True, blank=True)
    desc = models.CharField(max_length=500,null=True, blank=True)
    price = models.IntegerField(null=True, blank=True)
    # image = models.FileField(upload_to="product_image",max_length=250, null=True, default=None,validators=[validate_file_size])
    enabled = models.BooleanField(default=True,null=True)
    # is_approved = models.BooleanField(default=False,null=True)
    # is_rejected = models.BooleanField(default=False,null=True)


    def __str__(self):
        return self.name

class CallbackRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True, blank=True)
    service = models.ForeignKey('Service', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.PROTECT)
    requested_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return self.name


class Job(models.Model):
    recruiter = models.ForeignKey(Recruiter, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    job_description = models.TextField(null=True, blank=True)
    job_location = models.CharField(max_length=200,null=True, blank=True)
    job_type = models.CharField(max_length=200,null=True, blank=True)
    job_experience = models.CharField(max_length=200,null=True, blank=True)
    job_salary = models.CharField(max_length=200,null=True, blank=True)
    job_skills = models.CharField(max_length=200,null=True, blank=True)
    job_min_qualification = models.CharField(max_length=200,null=True, blank=True)
    job_posted_on = models.DateField(auto_now_add=True)
    # contact_email = models.EmailField()
    enabled = models.BooleanField(default=True,null=True)
    is_approved = models.BooleanField(default=False,null=True)
    is_rejected = models.BooleanField(default=False,null=True)

    def __str__(self):
        return self.job_title

    class Meta:
        verbose_name_plural = "Jobs"

class Applications(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    application_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return self.job.job_title
    
    class Meta:
        verbose_name_plural = "Applications"


class NoticeType(models.Model):
    name = models.CharField(max_length=100)
    code = AutoSlugField(populate_from='name', unique=True,null=True,default=None)
    # pagination_flag = models.BooleanField(default=True)
    # preview_url = models.URLField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'notices types'
        verbose_name_plural = 'notices types'

class Notice(models.Model):
    type = models.ForeignKey(NoticeType, on_delete=models.PROTECT)
    name = models.CharField(max_length=300)
    notice_date = models.DateField(null=True)
    enabled = models.BooleanField(null=True)
    file = models.FileField(upload_to=notice_file_upload_path,max_length=250, null=True, blank=True, default=None,validators=[validate_file_size])
  
    def __str__(self):
        return self.name
    
    class Meta:
        db_table = 'notices'
        verbose_name_plural = 'notices'

class VisitorCounter(models.Model):
    count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.count