from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from .models import Student, Department, Recruiter, Product, Service, Job, Applications, Notice
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.contrib.auth import logout
from django.contrib import messages
import random
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.urls import reverse



def index(request):
    products = Product.objects.filter(enabled=True).select_related('department').order_by('-id')
    services = Service.objects.filter(enabled=True).select_related('department').order_by('-id')
    latest_news = Notice.objects.filter(enabled=True).order_by('-id')
    student_count = Student.objects.count()
    recruiter_count = Recruiter.objects.count()
    product_count = Product.objects.count()
    service_count = Service.objects.count()

    # Extract all required product details
    product_details = []
    for product in products:
        product_details.append({
            'id': product.id,
            'name': product.name,
            'desc': product.desc, 
            'qty': product.qty,
            'price': product.price,
            'image': product.image.url,  # Use a default image if not uploaded
            'amazon_link': product.amazon_link,
            'flipkart_link': product.flipkart_link,
            'concerened_person': product.department.concerened_person,
            'phone_number': product.department.phone_number,
        })

    # Extract all required service details
    service_details = []
    for service in services:
        service_details.append({
            'id': service.id,
            'name': service.name,
            'desc': service.desc, 
            'duration': service.duration,
            'price': service.price,
            'concerened_person': service.department.concerened_person,
            'phone_number': service.department.phone_number,
        })


    context = {
        'products':product_details,
        'services':service_details,
        'latest_news':latest_news,
        'student_count':student_count,
        'recruiter_count':recruiter_count,
        'product_count':product_count,
        'service_count':service_count,
    }

    return render(request, 'index.html', context)

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
            mobile = request.POST['mobile']

            # Check if email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return render(request, 'register.html')

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
                'mobile':mobile
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
                    mobile = registration_data['mobile']

                    if user_type == 'student':
                        Student.objects.create(user=user, name=name, phone_number=mobile)
                    elif user_type == 'department':
                        Department.objects.create(user=user, department_name=name, phone_number=mobile)
                    elif user_type == 'recruiter':
                        Recruiter.objects.create(user=user, name=name, phone_number=mobile)

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
        # email = request.POST.get('email')
        password = request.POST.get('password')

        # Update admin user details
        # if name:
        #     admin_user.first_name = name
        # if email:
        #     admin_user.email = email
        #     admin_user.username = email  # Assuming email is also used as the username
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

    products = Product.objects.filter(is_rejected = False).order_by('-id')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            product.is_approved = True
            product.save()
        elif action == 'reject':
            product.is_rejected = True
            product.save()
        elif action == 'delete':
            product.delete()

        return redirect('admin_products')

    return render(request, 'admin_products.html', {'products': products})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_services(request):
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

    services = Service.objects.filter(is_rejected = False).order_by('-id')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        action = request.POST.get('action')
        service = get_object_or_404(Service, id=service_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            service.is_approved = True
            service.save()
        elif action == 'reject':
            service.is_rejected = True
            service.save()
        elif action == 'delete':
            service.delete()

        return redirect('admin_services')

    return render(request, 'admin_services.html', {'services': services})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def admin_jobs(request):
    # Check if the user is an admin (either staff user or custom admin model)
    if not (request.user.is_staff or hasattr(request.user, 'admin')):
        return redirect('login')  # If not an admin, redirect to login

    jobs = Job.objects.filter(is_rejected = False).order_by('-id')
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        action = request.POST.get('action')
        job = get_object_or_404(Job, id=job_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            job.is_approved = True
            job.save()
        elif action == 'reject':
            job.is_rejected = True
            job.save()
        elif action == 'delete':
            job.delete()

        return redirect('admin_jobs')

    return render(request, 'admin_jobs.html', {'jobs': jobs})

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
        concerened_person = request.POST.get('concerened_person')
        hod = request.POST.get('hod')
        # email = request.POST.get('email')
        password = request.POST.get('password')

        # Update User model fields
        # if email:
        #     admin_user.email = email
        #     admin_user.username = email  # Assuming email is also used as the username
        if password:
            admin_user.set_password(password)
        admin_user.save()

        # Update Department model fields
        if department_name:
            department.department_name = department_name
        if concerened_person:
            department.concerened_person = concerened_person
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
        'concerened_person':department.concerened_person,
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

    products = Product.objects.filter(department=department).order_by('-id')
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        # action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)
        
        # Handle actions based on the button clicked
        # if action == 'approve':
        #     product.is_approved = True
        #     product.save()
        # elif action == 'reject':
        #     product.delete()
        # elif action == 'delete':
        #     product.delete()

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
        amazon_link = request.POST['amazon']
        flipkart_link = request.POST['flipkart']

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
                return render(request, 'add_products.html', {'departments': departments})

        
        product = Product(
            name=name,
            department=department,
            qty=qty,
            desc=desc,
            price=price,
            image=image_path,
            amazon_link = amazon_link,
            flipkart_link = flipkart_link,
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
        product.amazon_link = request.POST['amazon']
        product.flipkart_link = request.POST['flipkart']
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
        # product.is_approved = False
        # product.is_rejected = False
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
def department_services(request):
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

    services = Service.objects.filter(department=department).order_by('-id')
    
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        action = request.POST.get('action')
        service = get_object_or_404(Service, id=service_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            service.is_approved = True
            service.save()
        elif action == 'reject':
            service.delete()
        elif action == 'delete':
            service.delete()

        return redirect('department_services')

    return render(request, 'department_services.html', {'services': services})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def add_services(request):
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
        duration = request.POST.get('duration')
        desc = request.POST.get('desc')
        price = request.POST.get('price')
        enabled = 'enabled' in request.POST  # Checkbox field
        # image = request.FILES.get('image')

        # Validate price and quantity
        try:
            if price and int(price) < 0:
                raise ValidationError("Price cannot be negative.")
        except ValueError:
            messages.error(request, "Invalid input for price.")
            return render(request, 'add_services.html', {'departments': departments})

        # Process image if exists
        # image_path = None
        # if image:
        #     fs = FileSystemStorage()
        #     try:
        #         image_path = fs.save(f'product_image/{image.name}', image)
        #     except Exception as e:
        #         messages.error(request, f"Error uploading image: {e}")
        #         return render(request, 'add_product.html', {'departments': departments})

        
        service = Service(
            name=name,
            department=department,
            duration=duration,
            desc=desc,
            price=price,
            # image=image_path,
            enabled=enabled
        )
        service.save()

        messages.success(request, "Service added successfully!")
        return redirect('add_services')  # Redirect to the same page or to another page as needed

    return render(request, 'add_services.html')

@cache_control(no_store=True, must_revalidate=True)
@login_required
def edit_services(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a department

    if request.method == 'POST':
        # Handle form submission
        service_id = request.POST.get('service_id')
        try:
            service = Service.objects.get(id=service_id, department=department)
        except Service.DoesNotExist:
            messages.error(request, "Service not found or does not belong to your department.")
            return redirect('department_services')

        # Update service fields
        service.name = request.POST['name']
        service.qty = request.POST['duration']
        service.price = request.POST['price']
        service.desc = request.POST['desc']
        service.enabled = 'enabled' in request.POST

        # Handle image upload
        # image = request.FILES.get('image')
        # if image:
        #     fs = FileSystemStorage()
        #     try:
        #         product.image = fs.save(f'product_image/{image.name}', image)
        #     except Exception as e:
        #         messages.error(request, f"Error uploading image: {e}")
        #         return render(request, 'edit_products.html', {'product': product})
        service.is_approved = False
        service.is_rejected = False
        service.save()
        messages.success(request, "Service updated successfully!")
        return redirect(f"{reverse('edit_services')}?service_id={service.id}")

    else:
        # Handle GET request to render the edit form
        service_id = request.GET.get('service_id')
        try:
            service = Service.objects.get(id=service_id, department=department)
        except Service.DoesNotExist:
            messages.error(request, "Service not found or does not belong to your department.")
            return redirect('department_services')

        return render(request, 'edit_services.html', {'service': service})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def delete_services(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        department = Department.objects.get(user=request.user)
    except Department.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a department

    if request.method == 'POST':
        # Handle form submission
        service_id = request.POST.get('service_id')  # Changed to POST
        try:
            service = Service.objects.get(id=service_id, department=department)
        except Service.DoesNotExist:
            messages.error(request, "Service not found or does not belong to your department.")
            return redirect('department_services')

        service.delete()
        messages.success(request, "Service deleted successfully!")
        return redirect('department_services')

    return render(request, 'department_services.html')
    

@cache_control(no_store=True, must_revalidate=True)
@login_required
def student_dashboard(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        student = Student.objects.get(user=request.user)
        print(f"Student found: {student.name}")
    except Student.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"
  
    return render(request, 'student_dashboard.html', {'student': student})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def student_profile(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        student = Student.objects.get(user=request.user)
        print(f"Student found: {student.name}")
    except Student.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    # Get the logged-in user
    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    student, created = Student.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        # Retrieve data from the POST request
        name = request.POST.get('name')
        course_name = request.POST.get('cname')
        branch_name = request.POST.get('bname')
        semester = request.POST.get('semester')
        enrollment_number = request.POST.get('enumber')
        roll_number = request.POST.get('rnumber')
        gender = request.POST.get('gender')
        date_of_birth = request.POST.get('dob')
        course_starting_year = request.POST.get('startYear')
        course_ending_year = request.POST.get('endYear')
        profile_tagline = request.POST.get('tagline')
        profile_summary = request.POST.get('summary')
        experience = request.POST.get('experience')
        skills = request.POST.get('skills')
        resume = request.POST.get('resume')
        linkedin = request.POST.get('linkedin')
        github = request.POST.get('github')
        website = request.POST.get('website')
        phone_number = request.POST.get('phone')
        # email = request.POST.get('email')
        password = request.POST.get('password')

        # Update User model fields
        # if email:
        #     admin_user.email = email
        #     admin_user.username = email  # Assuming email is also used as the username
        if password:
            admin_user.set_password(password)
        admin_user.save()

        # Update Department model fields
        # Update Student model fields
        if name:
            student.name = name
        if course_name:
            student.course_name = course_name
        if branch_name:
            student.branch_name = branch_name
        if semester:
            student.semester = semester
        if enrollment_number:
            student.enrollment_number = enrollment_number
        if roll_number:
            student.roll_number = roll_number
        if gender:
            student.gender = gender
        if date_of_birth:
            student.date_of_birth = date_of_birth
        if course_starting_year:
            student.course_starting_year = course_starting_year
        if course_ending_year:
            student.course_ending_year = course_ending_year
        if profile_tagline:
            student.profile_tagline = profile_tagline
        if profile_summary:
            student.profile_summary = profile_summary
        if experience:
            student.experience = experience
        if skills:
            student.skills = skills
        if resume:
            student.resume = resume
        if linkedin:
            student.linkedin = linkedin
        if github:
            student.github = github
        if website:
            student.website = website
        if phone_number:
            student.phone_number = phone_number
        student.save()

        # Show a success message
        messages.success(request, 'Profile updated successfully.')

        # Redirect to avoid re-submitting form on page refresh
        return redirect('student_profile')

    # Re-fetch the updated data after saving (ensure the latest values are passed)
    student.refresh_from_db()
    admin_user.refresh_from_db()

    # Send user and department data to the template
    return render(request, 'student_profile.html', {
        'name': student.name,
        'course_name': student.course_name,
        'branch_name': student.branch_name,
        'semester': student.semester,
        'enrollment_number': student.enrollment_number,
        'roll_number': student.roll_number,
        'gender': student.gender,
        'date_of_birth': student.date_of_birth,
        'course_starting_year': student.course_starting_year,
        'course_ending_year': student.course_ending_year,
        'profile_tagline': student.profile_tagline,
        'profile_summary': student.profile_summary,
        'experience': student.experience,
        'skills': student.skills,
        'resume': student.resume,
        'linkedin': student.linkedin,
        'github': student.github,
        'website': student.website,
        'phone_number': student.phone_number,
        'email': request.user.email,  # Include email from User model
    })


@cache_control(no_store=True, must_revalidate=True)
@login_required
def student_jobs(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
        
    try:
        # Ensure the user is a department user
        student = Student.objects.get(user=request.user)
        print(f"Student found: {student.name}")
    except Student.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    if request.method == "POST":
        # Handle the "Apply" form submission
        job_id = request.POST.get('job_id')
        student_id = request.POST.get('student_id')
        if student_id == str(student.id):  # Validate the student making the request
            try:
                job = Job.objects.get(id=job_id)
                # Check if the application already exists
                if not Applications.objects.filter(student=student, job=job).exists():
                    Applications.objects.create(student=student, job=job)
            except Job.DoesNotExist:
                pass  # Handle the case where the job does not exist
        return redirect('student_jobs')  # Redirect back to the jobs page after applying

    # Fetch all jobs and applied jobs for the student
    jobs = Job.objects.filter(is_approved=True, enabled=True)
    applied_jobs = Applications.objects.filter(student=student).values_list('job_id', flat=True)

    return render(request, 'student_jobs.html', {
        'jobs': jobs,
        'student': student,
        'applied_jobs': applied_jobs,
    })
    

@cache_control(no_store=True, must_revalidate=True)
@login_required
def recruiter_dashboard(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
        print(f"Recruiter found: {recruiter.name}")
    except Recruiter.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"
  
    return render(request, 'recruiter_dashboard.html', {'recruiter': recruiter})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def recruiter_profile(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
        print(f"Recruiter found: {recruiter.name}")
    except Recruiter.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    # Get the logged-in user
    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    recruiter, created = Recruiter.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        # Retrieve data from the POST request
        name = request.POST.get('name')
        hr_name = request.POST.get('hrname')
        hr_mail = request.POST.get('hremail')
        hr_mobile = request.POST.get('hrmobile')
        address = request.POST.get('address')
        gst = request.POST.get('gst')
        industry_type = request.POST.get('industrytype')
        company_phone_number = request.POST.get('companyphonenumber')
        password = request.POST.get('password')
        

        # Update User model fields
        # if email:
        #     admin_user.email = email
        #     admin_user.username = email  # Assuming email is also used as the username
        if password:
            admin_user.set_password(password)
        admin_user.save()

        # Update Department model fields
        # Update Student model fields
        if name:
            recruiter.name = name
        if hr_name:
            recruiter.hr_name = hr_name
        if hr_mail:
            recruiter.hr_mail = hr_mail
        if hr_mobile:
            recruiter.hr_mobile = hr_mobile
        if address:
            recruiter.address = address
        if gst:
            recruiter.gst = gst
        if industry_type:
            recruiter.industry_type = industry_type
        if company_phone_number:
            recruiter.company_phone_number = company_phone_number
        recruiter.save()

        # Show a success message
        messages.success(request, 'Profile updated successfully.')

        # Redirect to avoid re-submitting form on page refresh
        return redirect('recruiter_profile')

    # Re-fetch the updated data after saving (ensure the latest values are passed)
    recruiter.refresh_from_db()
    admin_user.refresh_from_db()

    # Send user and department data to the template
    return render(request, 'recruiter_profile.html', {
        'name': recruiter.name,
        'email': request.user.email,  # Include email from User model
        'hr_name': recruiter.hr_name,
        'hr_mail' : recruiter.hr_mail,
        'hr_mobile' : recruiter.hr_mobile,
        'address': recruiter.address,
        'gst': recruiter.gst,
        'industry_type': recruiter.industry_type,
        'company_phone_number' : recruiter.company_phone_number,      
    })

@cache_control(no_store=True, must_revalidate=True)
@login_required
def recruiter_jobs(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
        print(f"Recruiter found: {recruiter.name}")
    except Recruiter.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    # Get the logged-in user
    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    recruiter, created = Recruiter.objects.get_or_create(user=admin_user)
    
    jobs = Job.objects.filter(recruiter=recruiter).order_by('-id')
    
    if request.method == 'POST':
        job_id = request.POST.get('job_id')
        action = request.POST.get('action')
        job = get_object_or_404(Job, id=job_id)
        
        # Handle actions based on the button clicked
        if action == 'approve':
            job.is_approved = True
            job.save()
        elif action == 'reject':
            job.delete()
        elif action == 'delete':
            job.delete()

        return redirect('recruiter_jobs')

    return render(request, 'recruiter_jobs.html', {'jobs': jobs})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def add_jobs(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
        print(f"Recruiter found: {recruiter.name}")
    except Recruiter.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    recruiter, created = Recruiter.objects.get_or_create(user=admin_user)
    
    if request.method == 'POST':
        title = request.POST['title']
        desc = request.POST.get('desc')
        location = request.POST.get('location')
        job_type = request.POST.get('type')
        exp = request.POST.get('exp')
        salary = request.POST.get('salary')
        skill = request.POST.get('skill')
        post_date = request.POST.get('post_date')
        email = request.POST.get('email')
        enabled = 'enabled' in request.POST  # Checkbox field
        
                
        job = Job(
            recruiter=recruiter,
            job_title=title,
            job_description=desc,
            job_location=location,
            job_type=job_type,
            job_experience=exp,
            job_salary=salary,
            job_skills=skill,
            job_posted_on=post_date,
            contact_email = email,
            enabled=enabled
        )
        job.save()

        messages.success(request, "Job added successfully!")
        return redirect('add_jobs')  # Redirect to the same page or to another page as needed

    return render(request, 'add_jobs.html')

@cache_control(no_store=True, must_revalidate=True)
@login_required
def edit_jobs(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a department

    if request.method == 'POST':
        # Handle form submission
        job_id = request.POST.get('job_id')
        try:
            job = Job.objects.get(id=job_id, recruiter=recruiter)
        except Job.DoesNotExist:
            messages.error(request, "Job not found or does not belong to you.")
            return redirect('recruiter_jobs')

        # Update job fields
        job.job_title = request.POST['title']
        job.job_description = request.POST['desc']
        job.job_location = request.POST['location']
        job.job_type = request.POST['type']
        job.job_experience = request.POST['exp']
        job.job_salary = request.POST['salary']
        job.job_skils = request.POST['skill']
        job.job_poted_on = request.POST['post_date']
        job.contact_email = request.POST['email']
        job.enabled = 'enabled' in request.POST

       
        job.is_approved = False
        job.is_rejected = False
        job.save()
        messages.success(request, "Job updated successfully!")
        return redirect(f"{reverse('edit_jobs')}?job_id={job.id}")

    else:
        # Handle GET request to render the edit form
        job_id = request.GET.get('job_id')
        try:
            job = Job.objects.get(id=job_id, recruiter=recruiter)
        except Job.DoesNotExist:
            messages.error(request, "Job not found or does not belong to you.")
            return redirect('recruiter_jobs')

        return render(request, 'edit_jobs.html', {'job': job})

@cache_control(no_store=True, must_revalidate=True)
@login_required
def delete_jobs(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')

    try:
        # Ensure the user is a department user
        recuiter = Recruiter.objects.get(user=request.user)
    except Recruiter.DoesNotExist:
        return redirect('login')  # Redirect to login if the user is not part of a recruiter

    if request.method == 'POST':
        # Handle form submission
        job_id = request.POST.get('job_id')  # Changed to POST
        try:
            job = Job.objects.get(id=job_id, recruiter=recruiter)
        except Job.DoesNotExist:
            messages.error(request, "Job not found or does not belong to you.")
            return redirect('recruiter_jobs')

        job.delete()
        messages.success(request, "Job deleted successfully!")
        return redirect('recruiter_jobs')

    return render(request, 'recruiter_jobs.html')


@cache_control(no_store=True, must_revalidate=True)
@login_required
def applied_jobs(request):
    if request.user.is_staff:
        # If the user is an admin, redirect them to the admin dashboard
        return redirect('admin_dashboard')
    
    try:
        # Ensure the user is a department user
        recruiter = Recruiter.objects.get(user=request.user)
        print(f"Recruiter found: {recruiter.name}")
    except Recruiter.DoesNotExist:
        # If the user is not a department user, redirect to login or show an error
        return redirect('login')  # Or show a message saying "You are not a department"

    # Get the logged-in user
    admin_user = request.user
    
    # Fetch or create a Department entry for the current user
    recruiter, created = Recruiter.objects.get_or_create(user=admin_user)
    
    jobs = Job.objects.filter(recruiter=recruiter).order_by('-id')

    # Get all applications for the recruiter's jobs
    applications = Applications.objects.filter(job__recruiter=recruiter).select_related('job', 'student')

    # Prepare the context data
    context = {
        'recruiter': recruiter,
        'jobs': jobs,
        'applications': applications,
    }

    # Render the template
    return render(request, 'applied_jobs.html', context)