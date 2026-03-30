"""
URL Configuration for Accounts App

This module defines all URL patterns for user registration,
authentication, and admin management.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # =====================
    # Registration URLs
    # =====================
    path('register/', views.register, name='register'),
    path('registration-success/', views.registration_success, name='registration_success'),
    
    # =====================
    # Authentication URLs
    # =====================
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('admin/login/', views.AdminLoginView.as_view(), name='admin_login'),
    path('logout/', views.SecureLogoutView.as_view(), name='logout'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
         name='password_reset_complete'),
    
    # =====================
    # User Dashboard URLs
    # =====================
    path('dashboard/', views.user_dashboard, name='dashboard'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    
    # =====================
    # Admin URLs
    # =====================
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/batch-approve/', views.admin_batch_approve, name='admin_batch_approve'),
    path('admin/user/<int:profile_id>/', views.admin_view_user, name='admin_view_user'),
    path('admin/user/<int:profile_id>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('admin/user/<int:profile_id>/approve/', views.admin_approve_user, name='admin_approve_user'),
    path('admin/user/<int:profile_id>/reject/', views.admin_reject_user, name='admin_reject_user'),
    path('admin/user/<int:profile_id>/delete/', views.admin_delete_user, name='admin_delete_user'),
    path('admin/activity-logs/', views.user_activity_logs, name='user_activity_logs'),
]
