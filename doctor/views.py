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
    users = CustomUser.objects.filter(is_superuser=False).count()
    doctors = CustomDoctor.objects.all().count()
    products = Product.objects.all().count()

    return render(request,'admin_dashboard.html',{'current_user': request.user, "users": users,'doctors':doctors,'products':products})


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


#admin appoinment manage
def admin_appointment_list(request):
    consultations = Consultation.objects.select_related('user', 'doctor').order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'admin_appoinment_manage.html', {
        'consultations': consultations,
    })




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


from app.models import Order
def admin_orders_list(request):
    query = request.GET.get('q')
    if query:
        orders = Order.objects.filter(order_number__icontains=query)
    else:
        orders = Order.objects.all().order_by('-ordered_at')

    return render(request, 'admin_orders_list.html', {'orders': orders})


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
                return redirect('doctor_profile',doctor_id=doctor.id) 
            else:
                messages.error(request, "Invalid password.")
        except CustomDoctor.DoesNotExist:
            messages.error(request, "Doctor with this name does not exist.")

    return render(request, 'doctor_login.html')



from django.utils.timezone import now
from django.db.models import Min

def doctor_profile(request,doctor_id):
    doctor = get_object_or_404(CustomDoctor, id=doctor_id)

    consultations = Consultation.objects.filter(doctor=doctor).order_by('appointment_date', 'appointment_time')
    pending_count = Consultation.objects.filter(doctor=doctor, status='pending').count()

    # Get current month and year
    today = now().date()
    current_month = today.month
    current_year = today.year

    first_consults = (
        Consultation.objects.filter(doctor=doctor)
        .values('user')
        .annotate(first_date=Min('appointment_date'))
    )
    
    new_patients_this_month = sum(
        1 for fc in first_consults
        if fc['first_date'].month == current_month and fc['first_date'].year == current_year
    )


    context = {
        'consultations': consultations,
        'doctor': doctor,
        'pending_count': pending_count,
        'new_patients_count': new_patients_this_month,

    }
    return render(request, 'doctor_profile.html', context)


def patient_history(request, doctor_id):
    doctor = get_object_or_404(CustomDoctor, id=doctor_id)

    history = Consultation.objects.filter(doctor=doctor).order_by('-appointment_date')
    

    context = {
        'consultations': history,
        'doctor': doctor,
    }
    return render(request, 'patient_history.html', context)




def doctor_logout(request):
    logout(request)
    return redirect("/")


from app.models import Consultation
from app.models import Notification
from django.shortcuts import get_object_or_404


def approve_appointment(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    if request.method == 'POST':
        consultation.status = 'confirmed'
        consultation.save()
        
        # Create notification
        Notification.objects.create(
            user=consultation.user,
            doctor=consultation.doctor,
            consultation=consultation,
            message=f"Your appointment with Dr. {consultation.doctor.name} on {consultation.appointment_date} has been approved!",
            notification_type='appointment_approved'
        )
        
        messages.success(request, "Appointment approved and notification sent to patient.")
    return redirect('doctor_profile',doctor_id=consultation.doctor.id)


def decline_appointment(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    if request.method == 'POST':
        consultation.status = 'cancelled'
        consultation.save()
    return redirect('doctor_profile',doctor_id=consultation.doctor.id)


from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse

def export_orders(request):
    # Get data
    orders = Order.objects.prefetch_related('items', 'user').all()
    
    # Render the HTML template with context
    template = get_template('admin_orders_pdf.html')  # You must create this template
    html = template.render({'orders': orders})
    
    # Prepare PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="orders.pdf"'

    # Create PDF
    pisa_status = pisa.CreatePDF(BytesIO(html.encode('UTF-8')), dest=response, encoding='UTF-8')
    
    # Return error if any
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    
    return response



from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=settings.GOOGLE_API_KEY)

# Initialize the Gemini model
# You can choose different models like "gemini-pro", "gemini-1.5-flash", etc.
# Check the Gemini API documentation for available models.
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[]) # For maintaining conversation history

@csrf_exempt # Use this carefully for API endpoints, consider Django's CSRF tokens for forms
def chat_with_gemini(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_message = data.get("message")

            if not user_message:
                return JsonResponse({"error": "No message provided"}, status=400)

            # Send message to Gemini and get response
            response = chat.send_message(user_message)
            bot_reply = response.text

            return JsonResponse({"reply": bot_reply})

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"message": "Send a POST request with a 'message' to chat with Gemini."}, status=200)


def chat_page_doctor(request):
    return render(request, 'chatbot_page.html')