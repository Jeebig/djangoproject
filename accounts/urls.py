from django.urls import path
from django.contrib.auth.views import LoginView
from . import views
from .forms import CustomAuthenticationForm

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(
        template_name='accounts/login.html',
        authentication_form=CustomAuthenticationForm
    ), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile-user'),
    path('follow/<str:username>/', views.follow_toggle_view, name='follow-toggle'),
    path('followers/<str:username>/', views.followers_view, name='followers'),
    path('following/<str:username>/', views.following_view, name='following'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-read/', views.notifications_mark_read, name='notifications-mark-read'),
]