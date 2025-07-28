from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model,authenticate, login,logout
from django.views.decorators.csrf import csrf_protect
from .models import CustomUser,PasswordReset,Cart,Consultation,OrderItem,Order
from django.urls import reverse
from django.core.mail import EmailMessage
from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.http import JsonResponse
from doctor.models import CustomDoctor
import razorpay


User = get_user_model()

@csrf_protect
def user_registration(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        age = request.POST.get('age')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')
        state = request.POST.get('state')
        country = request.POST.get('country')

        if not all([username, email, password, confirm_password]):
            messages.error(request, "All required fields must be filled.")
            return redirect('register')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('register')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username is already in use.")
            return redirect('register')

        CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            age=age,
            phone_number=phone_number,
            address=address,
            pincode=pincode,
            state=state,
            country=country
        )
        messages.success(request, "Registration successful. Please log in.")
        return redirect('login')

    return render(request, 'register.html')


def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')


        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request,'login.html')

        
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('user_landing')
        else:   
            messages.error(request, "Invalid email or password.")
            return redirect('login')

    return render(request, 'login.html')



def edit_profile_user(request, user_id):
    user_to_edit = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        user_to_edit.username = request.POST.get('username', user_to_edit.username)
        user_to_edit.email = request.POST.get('email', user_to_edit.email)
        user_to_edit.age = request.POST.get('age', user_to_edit.age)
        user_to_edit.phone_number = request.POST.get('phone_number', user_to_edit.phone_number)
        user_to_edit.address = request.POST.get('address', user_to_edit.address)
        user_to_edit.pincode = request.POST.get('pincode', user_to_edit.pincode)
        user_to_edit.state = request.POST.get('state', user_to_edit.state)
        user_to_edit.country = request.POST.get('country', user_to_edit.country)

        user_to_edit.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile', user_id=user_to_edit.id)

    return render(request, 'edit_profile_user.html', {'user': user_to_edit})

# Users product management

from doctor.models import Product

def user_landing(request):
    products = Product.objects.all().order_by('-created_at')
    return render(request, 'user_landing.html', {'products': products})



def landing_page(request):
    return render(request,'landing_page.html')



def about(request):
    return render(request,'about.html')


def contact(request):
    return render(request,'contact.html')


def profile(request,user_id):
    
    profiles = get_object_or_404(CustomUser, id=user_id)
    return render(request,'user_profile.html',{'profiles': profiles})



def logout_view(request):
    logout(request)
    return redirect('/')


def product_view(request,product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request,'product_view_user.html',{'product':product})


#Forget Password

def forget_password(request):
    
    if request.method =="POST":
        email = request.POST.get('email')

        try:
            user = CustomUser.objects.get(email=email)

            new_password_reset = PasswordReset(user=user)
            new_password_reset.save()

            password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})

            full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'

            email_body = f'Reset your password using the link below:\n\n\n{full_password_reset_url}'
        

            email_message = EmailMessage(
                'Reset your password',
                email_body,
                settings.EMAIL_HOST_USER,
                [email]
            )

            email_message.fail_silently = False
            email_message.send()

            return HttpResponseRedirect(reverse("password-reset-sent", kwargs={"reset_id": new_password_reset.reset_id}))
        
        except CustomUser.DoesNotExist:
            messages.error(request, f"No user with email '{email}' found")
            return redirect('forgot-password')

    return render(request,'forget_password.html')


def password_reset_sent(request,reset_id):

    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')


def reset_password(request,reset_id):
    
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)

        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            passwords_have_error = False

            if password != confirm_password:
                passwords_have_error = True
                messages.error(request, 'Passwords do not match')
            
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)

            if timezone.now() > expiration_time:
                passwords_have_error = True
                messages.error(request, 'Reset link has expired')

                password_reset_id.delete()

            if not passwords_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()

                password_reset_id.delete()

                messages.success(request, 'Password reset. Proceed to login')
                return redirect('login')
            
            else:
                return redirect('reset-password',reset_id=reset_id)

    
    
    except PasswordReset.DoesNotExist:
        
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    return render(request, 'reset_password.html',{'reset_id': reset_id})



#Cart Functionality

from .cart import Cart

def cart_detail(request):
    cart = Cart(request)
    return render(request, "cart.html", {"cart": cart})

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart = Cart(request)
    cart.add(product,quantity=quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Product added', 'count': cart.count()})

    return redirect("cart_detail")


def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    cart.remove(product)
    messages.success(request, f'"{product.name}" was removed from your cart.')
    return redirect("cart_detail")


def cart_update(request, product_id):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        product = get_object_or_404(Product, id=product_id)
        cart = Cart(request)
        cart.update(product, quantity)
        messages.success(request, f'Quantity updated for "{product.name}".')
    return redirect("cart_detail")



def cart_count(request):
    cart = Cart(request)
    return JsonResponse({'count': cart.count()})


#Razorpay

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

def create_razorpay_order(request):
    cart = Cart(request)
    if cart.count() == 0:
        return JsonResponse({'error': 'Cart is empty'}, status=400)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    total_amount = int(cart.total_price() * 100)

    payment = client.order.create({
        "amount": total_amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    request.session['razorpay_order_id'] = payment["id"]

    return JsonResponse({
        "order_id": payment["id"],
        "amount": total_amount,
        "currency": "INR",
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })


@csrf_exempt
def payment_success(request):
    data = json.loads(request.body)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    params_dict = {
        'razorpay_order_id': data['razorpay_order_id'],
        'razorpay_payment_id': data['razorpay_payment_id'],
        'razorpay_signature': data['razorpay_signature']
    }

    try:
        client.utility.verify_payment_signature(params_dict)
        request.session['payment_success'] = True
        request.session['razorpay_payment_id'] = data['razorpay_payment_id']
        return JsonResponse({"redirect_url": reverse('payment_success_redirect')})
    except razorpay.errors.SignatureVerificationError:
        return JsonResponse({"message": "Payment verification failed."}, status=400)


def payment_success_redirect(request):
    if request.session.get('payment_success'):
        cart = Cart(request)
        user = request.user

        address = user.address if user.address else "No address provided"

        order = Order.objects.create(
            user=user,
            order_number=f"ORD-{int(timezone.now().timestamp())}",
            address=address,
            status='Placed',
            razorpay_order_id=request.session.get('razorpay_order_id', ''),
            razorpay_payment_id=request.session.get('razorpay_payment_id', '')
        )

        for item in cart:
            OrderItem.objects.create(
                order=order,
                product_id=item['id'],
                quantity=item['quantity'],
                price=item['price']
            )

            # 2. Reduce Product quantity
            product = Product.objects.get(id=item['id'])
            if product.quantity >= item['quantity']:
                product.quantity -= item['quantity']
                product.save()
            
            else:
                pass

        cart.clear()
        messages.success(request, "Payment successful and order placed!")

        # Clean up session
        for key in ['payment_success', 'razorpay_order_id', 'razorpay_payment_id']:
            if key in request.session:
                del request.session[key]

        return redirect('order_detail', order_id=order.id)

    return redirect('cart_detail')


def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items'), id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})


def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status == 'Placed':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, "Your order has been cancelled.")
    else:
        messages.error(request, "This order cannot be cancelled.")

    return redirect('order_detail', order_id=order.id)


def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    return render(request, 'orders/order_history.html', {'orders': orders})



#Pdf Download

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

def order_invoice_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    template_path = 'invoice_template.html'
    context = {'order': order}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_number}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

#Product Search

def product_search(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(name__icontains=query)
    else:
        products = Product.objects.all()
    context = {'products': products, 'query': query}
    return render(request, 'user_landing.html', context)



#Chatbot

import openai
from django.conf import settings

openai.api_key = settings.OPENAI_API_KEY

def generate_llm_response(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful medical AI assistant. The user describes symptoms, and you suggest a doctor specialty, and recommend useful products briefly."},
            {"role": "user", "content": message},
        ],
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()



import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed."}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message")
        context = data.get("context", {})

        if not user_message:
            return JsonResponse({"error": "Message is required."}, status=400)

        user = request.user if request.user.is_authenticated else None
        response_text, updated_context = generate_bot_response(user_message, user=user, context=context)

        return JsonResponse({
            "response": response_text,
            "context": updated_context
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






from datetime import datetime
from dateutil.parser import parse as parse_datetime
from .models import CustomDoctor, Consultation, Product


import re

def generate_bot_response(message, user=None, context=None):
    if context is None:
        context = {}

    message_lower = message.lower()

    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening","hii"]
    if message_lower.strip() in greetings:
        return (
            "Hi there! 👋 I'm your medical assistant. Please tell me your symptoms or let me know if you'd like skincare suggestions or book an appointment.",
            context
        )

    # Small talk or polite phrases
    if message_lower in ["how are you", "what's up", "how's it going"]:
        return (
            "I'm great, thanks for asking! 😊 How can I help you today with your health concerns or skincare suggestions?",
            context
        )
    if message_lower in ["thanks", "thank you", "welcome"]:
        return (
            "Thank you for choosing medi ai",
            context
        )

    # Step 1: If waiting for appointment date/time
    if context.get('booking_step') == 'ask_date_time':
        dt = None
        try:
            dt = datetime.strptime(message.strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            try:
                dt = parse_datetime(message.strip())
            except Exception:
                dt = None
        if not dt:
            return (
                "Please provide the appointment date and time in this format: YYYY-MM-DD HH:MM (24-hour time).",
                context
            )
        
        # ✅ Prevent booking in the past
        if dt < datetime.now():
            return (
                "You cannot book an appointment in the past. Please provide a valid future date and time (YYYY-MM-DD HH:MM).",
                context
            )

        doctor_id = context.get('doctor_id')
        if not doctor_id or not user or not user.is_authenticated:
            context.clear()
            return (
                "Sorry, I couldn't process your booking. Please start again.",
                context
            )

        doctor = CustomDoctor.objects.filter(id=doctor_id, is_active=True).first()
        if not doctor:
            context.clear()
            return (
                "Sorry, the selected doctor is no longer available.",
                context
            )

        Consultation.objects.create(
            user=user,
            doctor=doctor,
            appointment_date=dt.date(),
            appointment_time=dt.time(),
            status='pending',
        )

        context.clear()  # clear after booking
        return (
            f"Your appointment with Dr. {doctor.name} has been booked for {dt.strftime('%Y-%m-%d %H:%M')}. Thank you!",
            context
        )

    # Step 2: Check if user confirms booking (yes)
    if message_lower in ['yes', 'yeah', 'yup', 'sure', 'ok', 'okay']:
        if context.get('booking_step') == 'awaiting_booking_confirmation' and context.get('doctor_id'):
            context['booking_step'] = 'ask_date_time'
            return (
                "Great! Please provide the appointment date and time in this format: YYYY-MM-DD HH:MM (24-hour time).",
                context
            )
        else:
            return (
                "Please describe your symptoms first, so I can recommend a doctor.",
                context
            )

    # --- New Step: Product recommendation based on skin type ---
    if "recommend a product" in message_lower or "skincare suggestion" in message_lower:
        context["awaiting_skin_type"] = True
        return ("Sure! Please tell me your skin type (e.g., oily skin, dry skin, etc.)", context)
    

    if context.get('awaiting_skin_type'):
        skin_types = ["dry skin", "oily skin", "sensitive skin", "combination skin", "normal skin","dry", "oily","sensitive","combination"]
        for skin_type in skin_types:
            if skin_type in message_lower:
                from .utils import skincare_by_skin_type
                
                products = skincare_by_skin_type(skin_type)

                context.clear()


                print(f"Products for {skin_type}: {products}")
                if products:
                    product_list = "\n\n".join(
                        [
                            f"{i+1}. {p['product_name']} (₹{p.get('price', 'N/A')}): {p.get('description', 'No description')[:50]}..."
                            for i, p in enumerate(products)
                        ]
                    )
                    return (
                        f"For {skin_type}, here are some recommended products:\n{product_list}\n\n"
                        "Would you like to consult a dermatologist too?",
                        context
                    )
                    
                else:
                    return (
                        f"Sorry, no products found for {skin_type}. Would you like to consult a dermatologist?",
                        context
                    )

        return (
            "Sorry, I didn't recognize that skin type. Please specify one of: dry skin, oily skin, sensitive skin, combination skin, or normal skin.",
            context
        )


    # Step 3: Match symptoms to specialization and doctors
    symptom_specialization_map = {
        # General Symptoms
        "fever": "General Physician",
        "fatigue": "General Physician",
        "weight loss": "General Physician",
        "weight gain": "General Physician",
        "headache": "Neurologist",
        "dizziness": "Neurologist",
        "blurred vision": "Neurologist",
        # Respiratory
        "cough": "Pulmonologist",
        "shortness of breath": "Pulmonologist",
        "wheezing": "Pulmonologist",
        "asthma": "Pulmonologist",
        "bronchitis": "Pulmonologist",
        "tuberculosis": "Pulmonologist",
        # Cardiology
        "chest pain": "Cardiologist",
        "high blood pressure": "Cardiologist",
        "palpitations": "Cardiologist",
        "heart attack": "Cardiologist",
        "arrhythmia": "Cardiologist",
        # Dermatology
        "skin rash": "Dermatologist",
        "acne": "Dermatologist",
        "pimples": "Dermatologist",
        "itching": "Dermatologist",
        "eczema": "Dermatologist",
        "psoriasis": "Dermatologist",
        "hair loss": "Dermatologist",
        "dry skin": "Dermatologist",
        "oily skin": "Dermatologist",
        # Gastroenterology
        "stomach pain": "Gastroenterologist",
        "acid reflux": "Gastroenterologist",
        "constipation": "Gastroenterologist",
        "diarrhea": "Gastroenterologist",
        "ulcer": "Gastroenterologist",
        "hepatitis": "Gastroenterologist",
        # Neurology
        "seizures": "Neurologist",
        "memory loss": "Neurologist",
        "numbness": "Neurologist",
        "stroke": "Neurologist",
        "parkinson": "Neurologist",
        "multiple sclerosis": "Neurologist",
        # Endocrinology
        "diabetes": "Endocrinologist",
        "thyroid": "Endocrinologist",
        "hormone imbalance": "Endocrinologist",
        "obesity": "Endocrinologist",
        # Orthopedics
        "joint pain": "Orthopedist",
        "back pain": "Orthopedist",
        "arthritis": "Orthopedist",
        "fracture": "Orthopedist",
        "sprain": "Orthopedist",
        # Psychiatry
        "depression": "Psychiatrist",
        "anxiety": "Psychiatrist",
        "insomnia": "Psychiatrist",
        "bipolar disorder": "Psychiatrist",
        "schizophrenia": "Psychiatrist",
        # Ophthalmology
        "eye pain": "Ophthalmologist",
        "vision loss": "Ophthalmologist",
        "red eyes": "Ophthalmologist",
        "dry eyes": "Ophthalmologist",
        "cataract": "Ophthalmologist",
        # ENT (Ear, Nose, Throat)
        "ear pain": "ENT Specialist",
        "sinusitis": "ENT Specialist",
        "sore throat": "ENT Specialist",
        "hoarseness": "ENT Specialist",
        "hearing loss": "ENT Specialist",
        # Urology
        "urinary tract infection": "Urologist",
        "kidney stones": "Urologist",
        "prostate issues": "Urologist",
        # Gynecology
        "menstrual pain": "Gynecologist",
        "pregnancy": "Gynecologist",
        "breast pain": "Gynecologist",
        "infertility": "Gynecologist",
        # Pediatrics
        "child fever": "Pediatrician",
        "child cough": "Pediatrician",
        "child rash": "Pediatrician",
        # Dentistry
        "toothache": "Dentist",
        "gum bleeding": "Dentist",
        "cavity": "Dentist",
        # Rheumatology
        "lupus": "Rheumatologist",
        "fibromyalgia": "Rheumatologist",
        "vasculitis": "Rheumatologist",
        # Immunology / Allergies
        "allergy": "Immunologist",
        "asthma": "Immunologist",
        "autoimmune": "Immunologist",
        # Others
        "cancer": "Oncologist",
        "tumor": "Oncologist",
    }

    matched_specialization = None
    sorted_symptoms = sorted(symptom_specialization_map.items(), key=lambda x: -len(x[0]))
    for symptom, specialization in sorted_symptoms:
        if symptom in message_lower:
            matched_specialization = specialization
            break

    if matched_specialization:
        doctors = CustomDoctor.objects.filter(
            specialization__iexact=matched_specialization,
            is_active=True
        )
        if doctors.exists():
            doctor = doctors.first()
            doctor_list = "\n".join([f"- Dr. {doc.name} ({doc.email})" for doc in doctors])

            # Save context for next step: ask booking confirmation
            context.update({
                'booking_step': 'awaiting_booking_confirmation',
                'specialization': matched_specialization,
                'doctor_id': doctor.id,
            })

            return (
                f"Based on your symptoms, you should consult a **{matched_specialization}**.\n\n"
                f"Here are some available doctors:\n{doctor_list}\n\n"
                "Would you like to book an appointment?",
                context
            )
        else:
            return (
                f"Based on your symptoms, you should consult a **{matched_specialization}**, "
                "but currently there are no active doctors in this category. "
                "Please check again later or contact support.",
                context
            )
        
    

    # If no match and not booking step or skin type awaiting
    return (
        "I'm not sure which specialization fits your symptoms. Could you describe them a bit more?",
        context
    )






def chat_page(request):
    return render(request, 'chatbot.html')



#product recommendation
from .utils import skincare_by_skin_type

def recommend_products(request):
    recommendations = []
    skin_type = request.GET.get('skin_type', '')
    
    if skin_type:
        recommendations = skincare_by_skin_type(skin_type, num_products=5)

    return render(request, "skin_type_products.html", {
        "recommendations": recommendations,
        "skin_type": skin_type,
    })


import os
import pandas as pd
from django.conf import settings
from django.shortcuts import render, Http404


# def product_detail_csv(request, pk):
#     file_path = os.path.join(settings.BASE_DIR, 'app', 'export_skincare.csv')
#     try:
#         df = pd.read_csv(file_path)

#         # Find the product with the given pk (assuming 'id' column in CSV)
#         product_row = df[df['id'] == pk]

#         if product_row.empty:
#             raise Http404("Product not found")

#         product = product_row.iloc[0].to_dict()

#         return render(request, "product_detail.html", {"product": product})

#     except FileNotFoundError:
#         raise Http404("Data file not found")


from .models import ChatRoom, ChatMessage, Notification
from django.shortcuts import render, get_object_or_404

#chat 
def chat_room(request, consultation_id):
    consultation = get_object_or_404(Consultation, id=consultation_id)
    chat_room, created = ChatRoom.objects.get_or_create(consultation=consultation)
    messages = ChatMessage.objects.filter(room=chat_room).order_by('timestamp')
    
    # Mark notifications as read
    Notification.objects.filter(
        consultation=consultation,
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'chatroom.html', {
        'room': chat_room,
        'messages': messages,
        'consultation': consultation
    })



def send_message(request, room_id):
    if request.method == 'POST':
        room = get_object_or_404(ChatRoom, id=room_id)
        message = request.POST.get('message', '').strip()
        
        if message:
            if hasattr(request.user, 'customdoctor'):
                # Doctor is sending
                ChatMessage.objects.create(
                    room=room,
                    sender_doctor=request.user.customdoctor,
                    message=message
                )
            else:
                # Patient is sending
                ChatMessage.objects.create(
                    room=room,
                    sender=request.user,
                    message=message
                )
            
            return JsonResponse({'status': 'ok'})
    
    return JsonResponse({'status': 'error'}, status=400)


def notification_list(request):
    notifications = Notification.objects.all().order_by('-created_at')

    return render(request, 'notifications.html', {'notifications': notifications})



def appointment_list(request):
    consultations = Consultation.objects.select_related('doctor').all().order_by('-booked_at')
    return render(request, 'appointments_list.html', {'consultations': consultations})


def cancel_appointment(request, pk):
    consultation = get_object_or_404(Consultation, pk=pk)
    consultation.status = 'cancelled'
    consultation.save()
    return redirect('appointment_list')






