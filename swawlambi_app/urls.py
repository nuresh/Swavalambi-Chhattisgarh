from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('register/student/', views.register_student, name='register_student'),
    path('register/department/', views.register_department, name='register_department'),
    path('register/recruiter/', views.register_recruiter, name='register_recruiter'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/department/', views.department_dashboard, name='department_dashboard'),
    path('dashboard/recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    # path('admin/approve/student/<int:student_id>/', views.approve_student, name='approve_student'),
    # path('admin/approve/department/<int:department_id>/', views.approve_department, name='approve_department'),
    # path('admin/approve/recruiter/<int:recruiter_id>/', views.approve_recruiter, name='approve_recruiter'),
]
