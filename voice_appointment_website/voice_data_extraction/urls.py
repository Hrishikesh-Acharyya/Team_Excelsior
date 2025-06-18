from django.urls import path
from . import views

urlpatterns = [
  path('transcribe/', views.AudioTranscriptionAPIView.as_view(), name='AudioTranscription'),
  path('structure_data/', views.StructureDataAPIView.as_view(), name='StructureData'),
]