from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Student, Department, Recruiter
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout
from django.contrib import messages


def index(request):
    return render(request, 'index.html')

def register(request):
    return render(request, 'register.html')

# def register_student(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         name = request.POST['name']
#         cname = request.POST['cname']
#         bname = request.POST['bname']
#         semester = request.POST['semester']
#         enumber = request.POST['enumber']
#         rnumber = request.POST['rnumber']
#         gender = request.POST['gender']
#         dob = request.POST['dob']
#         syear = request.POST['syear']
#         eyear = request.POST['eyear']
#         ptagline = request.POST['ptagline']
#         psummary = request.POST['psummary']
#         experience = request.POST['experience']
#         skills = request.POST['skills']
#         resume = request.POST['resume']
#         linkedin = request.POST['linkedin']
#         github = request.POST['github']
#         website = request.POST['website']
#         mobile = request.POST['mobile']
        

#         user = User.objects.create_user(username=email, email=email, password=password)
#         Student.objects.create(user=user, name = name , course_name = cname, branch_name = bname, semester = semester, enrollment_number = enumber, roll_number = rnumber, gender = gender, date_of_birth = dob, course_starting_year = syear, course_ending_year = eyear, profile_tagline = ptagline, profile_summary = psummary, experience = experience, skills = skills, resume = resume, linkedin = linkedin, github = github, website = website, phone_number = mobile)
        
#         return redirect('login')
    
#     return render(request, 'register_student.html')

# def register_department(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         department_name = request.POST['dname']
#         head_of_department = request.POST['hod']

#         user = User.objects.create_user(username=email, email=email, password=password)
#         Department.objects.create(user=user, department_name=department_name, head_of_department=head_of_department)

#         return redirect('login')
    
#     return render(request, 'register_department.html')

# def register_recruiter(request):
#     if request.method == 'POST':
#         email = request.POST['email']
#         password = request.POST['password']
#         name = request.POST['name']
#         address = request.POST['address']
#         gst = request.POST['gst']
#         industry_name = request.POST['iname']

#         user = User.objects.create_user(username=email, email=email, password=password)
#         Recruiter.objects.create(user=user, name=name, address=address, gst=gst, industry_name=industry_name )

#         return redirect('login')

#     return render(request, 'register_recruiter.html')


# Unified Register View
def register(request):
    if request.method == 'POST':
        user_type = request.POST['user_type']
        email = request.POST['email']
        password = request.POST['password']
        name = request.POST['name']

        # Create the user
        user = User.objects.create_user(username=email, email=email, password=password)
        user.is_active = False
        user.save()

        # Create additional records based on user type
        if user_type == 'student':
            Student.objects.create(user=user, name=name)
        elif user_type == 'department':
            Department.objects.create(user=user, department_name=name)  # Assuming department name is used for "name"
        elif user_type == 'recruiter':
            Recruiter.objects.create(user=user, name=name)

        return redirect('login')

    return render(request, 'register.html')



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

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_profile(request):
    if request.method == 'POST':
        # Get the logged-in admin user
        admin_user = request.user

        # Retrieve data from the POST request
        # name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Update admin user details
        # if name:
        #     admin_user.first_name = name
        if email:
            admin_user.email = email
            admin_user.username = email  # Assuming email is also used as the username
        if password:
            admin_user.set_password(password)

        admin_user.save()

        # Show a success message
        messages.success(request, 'Profile updated successfully.')

        # Redirect to avoid re-submitting form on page refresh
        return redirect('admin_profile')

    # Send admin name and email to the template
    return render(request, 'admin_profile.html', {
        'name': request.user.first_name,
        'email': request.user.email,
    })

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_users(request):
    users = User.objects.all().order_by('is_active', '-date_joined')
    user_details = []

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        user = get_object_or_404(User, id=user_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            user.is_active = True
            user.save()
        elif action == 'reject':
            user.delete()
        elif action == 'delete':
            user.delete()

        return redirect('admin_users')

    for user in users:
        user_type = None
        name = None

        # Determine the user type and fetch the respective name
        if hasattr(user, 'student'):
            user_type = 'Student'
            name = user.student.name
        elif hasattr(user, 'department'):
            user_type = 'Department'
            name = user.department.department_name
        elif hasattr(user, 'recruiter'):
            user_type = 'Recruiter'
            name = user.recruiter.name
        else:
            user_type = 'Admin'
            name = user.username  # Default to username if no specific name field is found

        user_details.append({
            'id': user.id,
            'name': name,
            'email': user.email,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'user_type': user_type,
        })

    return render(request, 'admin_users.html', {'users': user_details})


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


