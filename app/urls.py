from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.landing_page,name='landing_page'),
    path('register/',views.user_registration,name='register'),
    path('login/',views.user_login,name='login'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('profile/<int:user_id>/',views.profile,name='profile'),
    path('logout/',views.logout_view,name='logout'),
    path('user_landing/',views.user_landing,name='user_landing'),
    path('product_view/<int:product_id>/',views.product_view,name='product_view'),
    path('product_search/', views.product_search, name='product_search'),
    

    #forget password
    path('forgot-password/', views.forget_password, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.password_reset_sent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.reset_password, name='reset-password'),



    #Cart Functionalties

    path('cart_detail/', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart_count/', views.cart_count, name='cart_count'),

    #Razorpay
    path("create-order/", views.create_razorpay_order, name="create_razorpay_order"),
    path("payment-success/", views.payment_success, name="payment_success"),
    path("payment-success-redirect/", views.payment_success_redirect, name="payment_success_redirect"),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('order/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),


    #Pdf download
    path('order/<int:order_id>/invoice/', views.order_invoice_pdf, name='order_invoice_pdf'),




    #Chatbot
    path('chat/', views.chat_page, name='chat_page'),
    path('chat-api/', views.chat_api, name='chat_api'),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

