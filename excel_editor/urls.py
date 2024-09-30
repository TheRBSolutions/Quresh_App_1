from django.urls import path
from . import views

app_name = 'excel_editor'

urlpatterns = [
    path('upload/', views.upload_excel, name='upload_excel'),
    path('save-changes/', views.save_changes, name='save_changes'),
    path('image/<int:image_id>/', views.get_image, name='get_image'),
    path('export-pdf/', views.export_pdf, name='export_pdf'), 
]