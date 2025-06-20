from  .import views
from django.urls import path

urlpatterns = [
  path('', views.index, name='index'),
  path('book_appointment/', views.book_appointment, name='book_appointment'),
  path('create_appointment/', views.AppointmentCreateView.as_view(), name='create_appointment')
]