from django.contrib import admin
from .models import Student, Department, Recruiter

# Register your models here.
# admin.site.register(ADMIN)
# admin.site.register(STUDENT)

admin.site.register(Student)
admin.site.register(Department)
admin.site.register(Recruiter)
