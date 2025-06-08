from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from . models import CustomDoctor,Product
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from app.models import CustomUser
from django.http import HttpResponseForbidden
import re



#Admin 
def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            messages.error(request, "Need admin credentials to access this page.")
                
    return render(request, "admin_login.html")

  
def admin_logout(request):
    logout(request)
    return redirect("/")


def admin_dashboard(request):
    return render(request,'admin_dashboard.html',{'current_user': request.user})




#User management

def admin_user_manage(request):
    users = CustomUser.objects.filter(is_superuser=False)
    return render(request, 'user_list.html', {'users': users})


def view_users(request,user_id):
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return render(request, 'user_list.html')

    return render(request,'view_users.html',{'user': user})

    

def delete_user(request, user_id):
    if request.method == "POST":
        user = get_object_or_404(CustomUser, id=user_id)
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect("admin_user_manage")

    return HttpResponseForbidden("Invalid request method.")




#Doctor management
def admin_doctor_manage(request):
    users = CustomDoctor.objects.filter()
    return render(request, 'doctor_list.html', {'users': users})



def view_doctors(request,doctor_id):
    try:
        doctor = CustomDoctor.objects.get(id=doctor_id)
    except CustomDoctor.DoesNotExist:
        return render(request, 'doctor_list.html')

    return render(request,'view_doctor.html',{'doctor': doctor})

    

def delete_doctor(request, doctor_id):
    if request.method == "POST":
        user = get_object_or_404(CustomDoctor, id=doctor_id)
        user.delete()
        messages.success(request, "Doctor deleted successfully!")
        return redirect("admin_user_manage")

    return HttpResponseForbidden("Invalid request method.")

def product_list(request):
    selected_category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    products = Product.objects.all()

    if selected_category:
        products = products.filter(category=selected_category)

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    # Get unique category names
    categories = Product.objects.values_list('category', flat=True).distinct()

    context = {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'product_list.html', context)


def add_product(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        category = request.POST.get('category')
        ingredients = request.POST.get('ingredients')
        skin_type = request.POST.get('skin_type')
        price = request.POST.get('price')
        quantity = request.POST.get('quantity')
        stock = request.POST.get('stock')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        # Save to database
        Product.objects.create(
            product_id=product_id,
            name=name,
            category=category,
            ingredients=ingredients,
            skin_type=skin_type,
            price=price,
            quantity=quantity,
            stock_availability=stock,
            description=description,
            image=image
        )
        messages.success(request, f"Product '{name}' added successfully!")
        return redirect('product_list')

    return render(request, 'add_product.html')


def view_product(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request,'product_view.html',{'product':product})


def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.category = request.POST.get('category')
        product.price = request.POST.get('price')
        product.stock_availability = request.POST.get('stock_availability')
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('product_list')
    return render(request, 'edit_product.html', {'product': product})


def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully.')
    return redirect('product_list')


#Doctor
def doctor_register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact_number = request.POST.get('contact_number')
        license_number = request.POST.get('license_number')
        experience_years = request.POST.get('experience_years')
        specialization = request.POST.get('specialization')
        password = request.POST.get('password')
        image = request.FILES.get('image')

        # Check if required fields are filled
        if not all([name, email, contact_number, license_number, experience_years, specialization, password, image]):
            messages.error(request, "All fields are required.")
            return render(request, 'doctor_register.html')

        # Check if email is already used
        if CustomDoctor.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'doctor_register.html')

        # Check if name/username is already used
        if CustomDoctor.objects.filter(name=name).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'doctor_register.html')

        # Validate password
        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return render(request, 'doctor_register.html')

        if not re.search(r"[A-Z]", password) or not re.search(r"\d", password):
            messages.error(request, "Password must contain at least one uppercase letter and one number.")
            return render(request, 'doctor_register.html')

        try:
            hashed_password = make_password(password)

            CustomDoctor.objects.create(
                name=name,
                email=email,
                contact_number=contact_number,
                license_number=license_number,
                experience_years=experience_years,
                specialization=specialization,
                password=hashed_password,
                image=image
            )
            messages.success(request, "You have registered successfully.")
            return redirect('doctor_login')

        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            return render(request, 'doctor_register.html')

    return render(request, 'doctor_register.html')


def doctor_login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')

        if not name or not password:
            messages.error(request, "Both name and password are required.")
            return render(request, 'doctor_login.html')

        try:
            doctor = CustomDoctor.objects.get(name=name)
            if check_password(password, doctor.password):
                messages.success(request, f"Welcome, Dr. {doctor.name}!")
                return redirect('doctor_profile') 
            else:
                messages.error(request, "Invalid password.")
        except CustomDoctor.DoesNotExist:
            messages.error(request, "Doctor with this name does not exist.")

    return render(request, 'doctor_login.html')



def doctor_profile(request):
    return render(request,'doctor_profile.html')



def doctor_logout(request):
    logout(request)
    return redirect("/")


from app.models import Consultation

#Appoinment management
def appointments_list(request):
    print("View loaded")
    consultations = Consultation.objects.all().order_by('appointment_date', 'appointment_time')
    print(f"Consultations Query: {consultations.query}")  # Debug SQL query
    print(f"Consultations Count: {consultations.count()}")  # Debug count
    
    for consultation in consultations:
        print(f"Consultation: {consultation.id}, User: {consultation.user.username if consultation.user else 'None'}, Date: {consultation.appointment_date}, Time: {consultation.appointment_time}")
    
    context = {
        'consultations': consultations,
    }
    return render(request, 'doctor_profile.html', context)


def approve_appointment(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    if request.method == 'POST':
        consultation.status = 'confirmed'
        consultation.save()
    return redirect('doctor_profile')


def decline_appointment(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    if request.method == 'POST':
        consultation.status = 'cancelled'
        consultation.save()
    return redirect('doctor_profile')