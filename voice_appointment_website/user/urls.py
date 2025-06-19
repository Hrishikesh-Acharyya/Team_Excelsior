from django.urls import path
from . import views

urlpatterns = [
    path('api_register/', views.registerUser.as_view(), name='register_user'),
    path('register/', views.registerUserForm.as_view(), name='register_user_form'),
    path('login/', views.loginUser, name='login_user'),
]