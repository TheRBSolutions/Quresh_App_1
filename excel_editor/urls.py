from django.urls import path
from . import views

app_name = 'excel_editor'

urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('save/', views.save_data, name='save_data'),
]