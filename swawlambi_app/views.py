from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Student, Department, Recruiter, Product
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout
from django.contrib import messages
import random
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.urls import reverse



def index(request):
    return render(request, 'index.html')

otp_storage = {}

# Unified Register View
def register(request):
    if request.method == 'POST':
        step = request.POST.get('step', 'registration')

        if step == 'registration':
            # Step 1: Handle registration details
            user_type = request.POST['user_type']
            email = request.POST['email']
            password = request.POST['password']
            confirm_password = request.POST['confirm_password']
            name = request.POST['name']

            # Check if passwords match
            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'register.html')

            # Generate OTP
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp

            # Send OTP via email
            send_mail(
                'Your OTP for Registration',
                f'Your OTP is {otp}. Please enter this to complete your registration.',
                'admin@example.com',
                [email],
                fail_silently=False,
            )

            # Temporarily store registration details in session
            request.session['registration_data'] = {
                'user_type': user_type,
                'email': email,
                'password': password,
                'name': name,
            }

            messages.success(request, "OTP has been sent to your email.")
            return render(request, 'register.html', {'step': 'otp_verification', 'email': email})

        elif step == 'otp_verification':
            # Step 2: Handle OTP verification
            email = request.POST['email']
            entered_otp = request.POST['otp']

            if email in otp_storage and str(otp_storage[email]) == entered_otp:
                # OTP is correct, create the user
                registration_data = request.session.pop('registration_data', None)

                if registration_data:
                    user = User.objects.create_user(
                        username=registration_data['email'],
                        email=registration_data['email'],
                        password=registration_data['password']
                    )
                    user.is_active = False  # Activate user upon OTP verification
                    user.save()

                    # Create additional records based on user type
                    user_type = registration_data['user_type']
                    name = registration_data['name']

                    if user_type == 'student':
                        Student.objects.create(user=user, name=name)
                    elif user_type == 'department':
                        Department.objects.create(user=user, department_name=name)
                    elif user_type == 'recruiter':
                        Recruiter.objects.create(user=user, name=name)

                    messages.success(request, "Registration successful! Please login.")
                    return redirect('login')
            else:
                messages.error(request, "Invalid OTP. Please try again.")
                return render(request, 'register.html', {'step': 'otp_verification', 'email': email})

    return render(request, 'register.html', {'step': 'registration'})


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
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

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
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

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
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

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

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_products(request):
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

    products = Product.objects.all().order_by('-id')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            product.is_approved = True
            product.save()
        elif action == 'reject':
            product.delete()
        elif action == 'delete':
            product.delete()

        return redirect('admin_products')

    return render(request, 'admin_products.html', {'products': products})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def department_dashboard(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
        print(f"Department found: {department.department_name}")
    except Department.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"
  
    return render(request, 'department_dashboard.html', {'department': department})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def department_profile(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
        print(f"Department found: {department.department_name}")
    except Department.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    # Get the logged-in user
    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    department, created = Department.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        # Retrieve data from the POST request
        department_name = request.POST.get('department_name')
        hod = request.POST.get('hod')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Update User model fields
        if email:
            admin_user.email = email
            admin_user.username = email  # Assuming email is also used as the username
        if password:
            admin_user.set_password(password)
        admin_user.save()

        # Update Department model fields
        if department_name:
            department.department_name = department_name
        if hod:
            department.head_of_department = hod
        department.save()

        # Show a success message
        messages.success(request, 'Profile updated successfully.')

        # Redirect to avoid re-submitting form on page refresh
        return redirect('department_profile')

    # Re-fetch the updated data after saving (ensure the latest values are passed)
    department.refresh_from_db()
    admin_user.refresh_from_db()

    # Send user and department data to the template
    return render(request, 'department_profile.html', {
        'email': admin_user.email,
        'department_name': department.department_name,
        'hod': department.head_of_department,
    })


@cache_control(no_store=True, must_revalidate=True)
@login_required
def department_products(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
        print(f"Department found: {department.department_name}")
    except Department.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    products = Product.objects.all().order_by('-id')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            product.is_approved = True
            product.save()
        elif action == 'reject':
            product.delete()
        elif action == 'delete':
            product.delete()

        return redirect('department_products')

    return render(request, 'department_products.html', {'products': products})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def add_products(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
        print(f"Department found: {department.department_name}")
    except Department.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    department, created = Department.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        name = request.POST['name']
        qty = request.POST.get('qty')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        enabled = 'enabled' in request.POST  # Checkbox field
        image = request.FILES.get('image')

        # Validate price and quantity
        try:
            if qty and int(qty) < 0:
                raise ValidationError("Quantity cannot be negative.")
            if price and int(price) < 0:
                raise ValidationError("Price cannot be negative.")
        except ValueError:
            messages.error(request, "Invalid input for quantity or price.")
            return render(request, 'add_product.html', {'departments': departments})

        # Process image if exists
        image_path = None
        if image:
            fs = FileSystemStorage()
            try:
                image_path = fs.save(f'product_image/{image.name}', image)
            except Exception as e:
                messages.error(request, f"Error uploading image: {e}")
                return render(request, 'add_product.html', {'departments': departments})

        
        product = Product(
            name=name,
            department=department,
            qty=qty,
            desc=desc,
            price=price,
            image=image_path,
            enabled=enabled
        )
        product.save()

        messages.success(request, "Product added successfully!")
        return redirect('add_products')  # Redirect to the same page or to another page as needed

    return render(request, 'add_products.html')

@cache_control(no_store=True, must_revalidate=True)
@login_required
def edit_products(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a department

    if request.method == 'POST':
        # Handle form submission
        product_id = request.POST.get('product_id')
        try:
            product = Product.objects.get(id=product_id, department=department)
        except Product.DoesNotExist:
            messages.error(request, "Product not found or does not belong to your department.")
            return redirect('department_products')

        # Update product fields
        product.name = request.POST['name']
        product.qty = request.POST['qty']
        product.price = request.POST['price']
        product.desc = request.POST['desc']
        product.enabled = 'enabled' in request.POST

        # Handle image upload
        image = request.FILES.get('image')
        if image:
            fs = FileSystemStorage()
            try:
                product.image = fs.save(f'product_image/{image.name}', image)
            except Exception as e:
                messages.error(request, f"Error uploading image: {e}")
                return render(request, 'edit_products.html', {'product': product})
        product.is_approved = False
        product.save()
        messages.success(request, "Product updated successfully!")
        return redirect(f"{reverse('edit_products')}?product_id={product.id}")

    else:
        # Handle GET request to render the edit form
        product_id = request.GET.get('product_id')
        try:
            product = Product.objects.get(id=product_id, department=department)
        except Product.DoesNotExist:
            messages.error(request, "Product not found or does not belong to your department.")
            return redirect('department_products')

        return render(request, 'edit_products.html', {'product': product})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def delete_products(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a department

    if request.method == 'POST':
        # Handle form submission
        product_id = request.POST.get('product_id')  # Changed to POST
        try:
            product = Product.objects.get(id=product_id, department=department)
        except Product.DoesNotExist:
            messages.error(request, "Product not found or does not belong to your department.")
            return redirect('department_products')

        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect('department_products')

    return render(request, 'department_products.html')



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
def recruiter_dashboard(request):
    # Ensure user is a recruiter
    try:
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('login')  # Or show a message saying "You are not a recruiter"

    return render(request, 'recruiter_dashboard.html', {'recruiter': recruiter})


