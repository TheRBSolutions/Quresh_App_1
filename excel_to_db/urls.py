from django.urls import path
from . import views

app_name = 'excel_to_db'

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('generate_pdf/', views.generate_pdf, name='generate_pdf'),
    path('add_product/', views.add_product, name='add_product'),
    path('edit_product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('delete_product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('update_image/<int:product_id>/', views.update_image, name='update_image'),
]