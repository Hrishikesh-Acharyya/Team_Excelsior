from django.urls import path
from . import views

urlpatterns = [
  path('transcribe/', views.AudioTranscriptionAPIView.as_view(), name='AudioTranscription'),
]