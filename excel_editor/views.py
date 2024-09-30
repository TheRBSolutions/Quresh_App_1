from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from .forms import ExcelUploadForm
from .models import ExcelData, ExcelImage
from .excel_utils import process_excel_file
import json
import base64
import os
import logging

logger = logging.getLogger(__name__)

from django.shortcuts import render
from django.http import JsonResponse
from .forms import ExcelUploadForm
from .excel_utils import process_excel_file
import json
import logging

logger = logging.getLogger(__name__)

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                json_data, extracted_images = process_excel_file(excel_file)
                request.session['excel_data'] = json_data  # Store data in session
                return render(request, 'excel_editor/edit_data.html', {
                    'data': json_data,
                    'extracted_images': extracted_images
                })
            except ValueError as e:
                logger.error(f"Error processing Excel file: {str(e)}")
                return render(request, 'excel_editor/upload.html', {
                    'form': form,
                    'error_message': str(e)
                })
    else:
        form = ExcelUploadForm()
    return render(request, 'excel_editor/upload.html', {'form': form})

def save_changes(request):
    if request.method == 'POST':
        data = request.session.get('excel_data', [])
        for item in data:
            new_price = request.POST.get(f"price_{item['No']}")
            if new_price:
                item['Price'] = float(new_price)
        
        request.session['excel_data'] = data
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})

def get_image(request, image_id):
    image = get_object_or_404(ExcelImage, id=image_id)
    return HttpResponse(image.image, content_type='image/png')


from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from io import BytesIO

def export_pdf(request):
    if request.method == 'POST':
        selected_rows = json.loads(request.POST.get('selected_rows', '[]'))
        
        # Fetch the data for selected rows
        data = [['No', 'Information', 'Price']]
        for row in selected_rows:
            # Fetch the data for this row from your database
            # This is just an example, adjust according to your data structure
            excel_image = ExcelImage.objects.get(id=row)
            data.append([excel_image.number, excel_image.information, excel_image.price])

        # Create the PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(t)
        doc.build(elements)

        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    return HttpResponse("Invalid request method", status=400)