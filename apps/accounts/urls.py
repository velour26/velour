from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterPageView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),

    # Password reset flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='account/password_reset.html',
        email_template_name='email/password_reset.html',
        html_email_template_name='email/password_reset.html',
        subject_template_name='email/password_reset_subject.txt',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='account/password_reset_done.html',
    ), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='account/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='account/password_reset_complete.html',
    ), name='password_reset_complete'),
]
