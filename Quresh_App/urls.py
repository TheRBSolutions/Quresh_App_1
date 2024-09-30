from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('excel_to_db/', include('excel_to_db.urls')),
    path('excel-editor/', include('excel_editor.urls', namespace='excel_editor')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)