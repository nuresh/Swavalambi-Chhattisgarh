from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Student, Department, Recruiter
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout


def index(request):
    return render(request, 'index.html')

def register(request):
    return render(request, 'register.html')

def register_student(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        cname = request.POST['cname']
        bname = request.POST['bname']
        semester = request.POST['semester']
        enumber = request.POST['enumber']
        rnumber = request.POST['rnumber']
        gender = request.POST['gender']
        dob = request.POST['dob']
        syear = request.POST['syear']
        eyear = request.POST['eyear']
        ptagline = request.POST['ptagline']
        psummary = request.POST['psummary']
        experience = request.POST['experience']
        skills = request.POST['skills']
        resume = request.POST['resume']
        linkedin = request.POST['linkedin']
        github = request.POST['github']
        website = request.POST['website']
        mobile = request.POST['mobile']
        

        user = User.objects.create_user(username=email, email=email, password=password)
        Student.objects.create(user=user, name = name , course_name = cname, branch_name = bname, semester = semester, enrollment_number = enumber, roll_number = rnumber, gender = gender, date_of_birth = dob, course_starting_year = syear, course_ending_year = eyear, profile_tagline = ptagline, profile_summary = psummary, experience = experience, skills = skills, resume = resume, linkedin = linkedin, github = github, website = website, phone_number = mobile)
        
        return redirect('login')
    
    return render(request, 'register_student.html')

def register_department(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        department_name = request.POST['dname']
        head_of_department = request.POST['hod']

        user = User.objects.create_user(username=email, email=email, password=password)
        Department.objects.create(user=user, department_name=department_name, head_of_department=head_of_department)

        return redirect('login')
    
    return render(request, 'register_department.html')

def register_recruiter(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']
        address = request.POST['address']
        gst = request.POST['gst']
        industry_name = request.POST['iname']

        user = User.objects.create_user(username=email, email=email, password=password)
        Recruiter.objects.create(user=user, name=name, address=address, gst=gst, industry_name=industry_name )

        return redirect('login')

    return render(request, 'register_recruiter.html')

# Unified Login View
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on user roles
            if user.is_staff:  # Check if the user is a superuser (admin role)
                return redirect('admin_dashboard')
            elif hasattr(user, 'student'):  # User is a Student
                return redirect('student_dashboard')
            elif hasattr(user, 'department'):  # User is a Department
                return redirect('department_dashboard')
            elif hasattr(user, 'recruiter'):  # User is a Recruiter
                return redirect('recruiter_dashboard')
            else:
                return redirect('login')  # No role found, return to login page

        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'login.html')

def logout_view(request):  
    logout(request)
    request.session.flush()
    return redirect('login')  

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_dashboard(request):
    # # Check if the user is an admin (either staff user or custom admin model)
    # if not (request.user.is_staff or hasattr(request.user, 'admin')):
    #     return redirect('login')  # If not an admin, redirect to login

    # Now, only admins can access this page
    students = Student.objects.count()
    departments = Department.objects.count()
    recruiters = Recruiter.objects.count()

    return render(request, 'admin_dashboard.html', {
        'students': students,
        'departments': departments,
        'recruiters': recruiters
    })

# def approve_student(request, student_id):
#     student = Student.objects.get(id=student_id)
#     student.is_active = True
#     student.user.is_active = True  # Activate the user
#     student.user.save()
#     student.save()
#     return redirect('admin_dashboard')

# def approve_department(request, department_id):
#     department = Department.objects.get(id=department_id)
#     department.is_active = True
#     department.user.is_active = True  # Activate the user
#     department.user.save()
#     department.save()
#     return redirect('admin_dashboard')

# def approve_recruiter(request, recruiter_id):
#     recruiter = Recruiter.objects.get(id=recruiter_id)
#     recruiter.is_active = True
#     recruiter.user.is_active = True  # Activate the user
#     recruiter.user.save()
#     recruiter.save()
#     return redirect('admin_dashboard')

@cache_control(no_store=True, must_revalidate=True)
@login_required
def student_dashboard(request):
    # Ensure user is a student
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        return redirect('login')  # Or show a message saying "You are not a student"

    return render(request, 'student_dashboard.html', {'student': student})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def department_dashboard(request):
    # Ensure user is a department
    try:
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        return redirect('login')  # Or show a message saying "You are not a department"

    return render(request, 'department_dashboard.html', {'department': department})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def recruiter_dashboard(request):
    # Ensure user is a recruiter
    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('login')  # Or show a message saying "You are not a recruiter"

    return render(request, 'recruiter_dashboard.html', {'recruiter': recruiter})
