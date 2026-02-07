from django.urls import path
from django.contrib.auth import views as auth_views


from . import views


app_name = 'user-creation'
urlpatterns = [
    path('reg-2kp9w5/', views.SignUpView.as_view(), name='signup'),
    path('auth-7vm4x2/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]


