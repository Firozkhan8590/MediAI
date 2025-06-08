from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    #Doctor
    path('doctor_register/',views.doctor_register,name='doctor_register'),
    path('doctor_login/',views.doctor_login,name='doctor_login'),
    path('doctor_profile/',views.doctor_profile,name='doctor_profile'),
    path('doctor_logout/',views.doctor_logout,name='doctor_logout'),
    



    #Admin
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),

    #admin user manage
    path('admin_user_manage/',views.admin_user_manage,name='admin_user_manage'),
    path('view_users/<int:user_id>/',views.view_users,name='view_users'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),

    #admin doctor manage
    path('admin_doctor_manage/',views.admin_doctor_manage,name='admin_doctor_manage'),
    path('view_doctors/<int:doctor_id>/',views.view_doctors,name='view_doctors'),
    path('delete_doctor/<int:doctor_id>/', views.delete_doctor, name='delete_doctor'),


    #admin product manage
    path('product_list/', views.product_list, name='product_list'),
    path('add_product/', views.add_product, name='add_product'),
    path('view_product/<int:product_id>/', views.view_product, name='view_product'),
    path('doctor/edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('doctor/delete_product/<int:product_id>/', views.delete_product, name='delete_product'),


    #appoinment management
    path('appointments/', views.appointments_list, name='appointments_list'),
    path('appointments/<int:consultation_id>/approve/', views.approve_appointment, name='approve_appointment'),
    path('appointments/<int:consultation_id>/decline/', views.decline_appointment, name='decline_appointment'),

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)