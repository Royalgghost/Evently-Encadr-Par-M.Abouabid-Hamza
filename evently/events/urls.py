from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from . import views_event_management
from . import admin_views
from .direct_views import direct_create_event

urlpatterns = [
    # Basic views
    path('', views.home, name='home'),
    path('events/', views.EventListView.as_view(), name='events'),
    path('events/<slug:slug>/', views.EventDetailView.as_view(), name='event_detail'),
    
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='events/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='events/password_reset.html'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='events/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='events/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='events/password_reset_complete.html'), 
         name='password_reset_complete'),
    
    # Event management - Using a completely different URL path
    path('create-event/', direct_create_event, name='create_event'),
    path('events/<slug:slug>/update/', views_event_management.EventUpdateView.as_view(), name='update_event'),
    path('events/<slug:slug>/delete/', views_event_management.EventDeleteView.as_view(), name='delete_event'),
    
    # Venue management
    path('venues/new/', views_event_management.VenueCreateView.as_view(), name='create_venue'),
    path('venues/<int:pk>/update/', views_event_management.VenueUpdateView.as_view(), name='update_venue'),
    path('venues/<int:pk>/delete/', views_event_management.VenueDeleteView.as_view(), name='delete_venue'),
    
    # Event registration
    path('events/<slug:slug>/register/', views_event_management.register_for_event, name='register_for_event'),
    path('registration/<int:registration_id>/cancel/', views_event_management.cancel_registration, name='cancel_registration'),
    path('registration/<int:registration_id>/ticket/', views_event_management.generate_ticket, name='generate_ticket'),
    
    # Admin Dashboard - Changed from 'admin/' to 'dashboard/' to avoid conflict with Django admin
    path('dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/update-user-role/', admin_views.update_user_role, name='update_user_role'),
    path('dashboard/upload-image/', admin_views.upload_image, name='upload_image'),
    path('dashboard/delete-image/<int:image_id>/', admin_views.delete_image, name='delete_image'),
    path('dashboard/get-image-details/<int:image_id>/', admin_views.get_image_details, name='get_image_details'),
]
