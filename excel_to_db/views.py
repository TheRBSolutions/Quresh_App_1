from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Product
from .forms import ProductForm, ExcelUploadForm
import pandas as pd
from io import BytesIO
import os
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from PIL import Image as PILImage
import logging

logger = logging.getLogger(__name__)

def index(request):
    search_query = request.GET.get('search', '').strip()
    if search_query:
        products = Product.objects.filter(
            product_name__icontains=search_query
        ) | Product.objects.filter(
            unique_model_code__icontains=search_query
        ) | Product.objects.filter(
            specification__icontains=search_query
        )
    else:
        products = Product.objects.all()
    return render(request, 'excel_to_db/index.html', {'products': products, 'search_query': search_query})

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            if file.name.endswith('.xlsx'):
                file_path = os.path.join(settings.MEDIA_ROOT, file.name)
                with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                process_excel(file_path)
                os.remove(file_path)
                messages.success(request, 'Excel file processed successfully')
                return redirect('excel_to_db:index')
    else:
        form = ExcelUploadForm()
    return render(request, 'excel_to_db/upload_excel.html', {'form': form})

def generate_pdf(request):
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_ids')
        products = Product.objects.filter(id__in=product_ids)
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
        styles = getSampleStyleSheet()
        
        # Define column widths as percentages of the page width
        page_width = landscape(letter)[0] - 40  # Subtracting left and right margins
        col_widths = [
            0.15 * page_width,  # Product
            0.08 * page_width,  # No.
            0.15 * page_width,  # Unique Model Code
            0.27 * page_width,  # Specification
            0.10 * page_width,  # Price
            0.25 * page_width,  # Image
        ]
        
        # Create table data
        table_data = [["Product", "No.", "Unique Model Code", "Specification", "Price", "Image"]]  # Header row
        
        for product in products:
            row = [
                Paragraph(product.product_name, styles['Normal']),
                str(product.no),
                Paragraph(product.unique_model_code, styles['Normal']),
                Paragraph(product.specification, styles['Normal']),
                f"${product.price:.2f}",
                ""  # Placeholder for image
            ]
            if product.image:
                img_buffer = BytesIO(product.image.read())
                img = PILImage.open(img_buffer)
                img_width, img_height = img.size
                aspect = img_height / float(img_width)
                
                max_width = col_widths[-1]  # Use the width of the image column
                img_width = min(img_width, max_width)
                img_height = img_width * aspect
                
                temp_img = BytesIO()
                img.save(temp_img, format='PNG')
                temp_img.seek(0)
                
                img = ReportLabImage(temp_img, width=img_width, height=img_height)
                row[-1] = img  # Replace placeholder with actual image
            
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('WORDWRAP', (0, 0), (-1, -1)),  # Enable word wrapping for all cells
        ]))
        
        # Build PDF
        elements = [table]
        doc.build(elements)
        
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully')
            return redirect('excel_to_db:index')
    else:
        form = ProductForm()
    return render(request, 'excel_to_db/add_product.html', {'form': form})

def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully')
            return redirect('excel_to_db:index')
    else:
        form = ProductForm(instance=product)
    return render(request, 'excel_to_db/edit_product.html', {'form': form, 'product': product})

def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, 'Product deleted successfully')
    return redirect('excel_to_db:index')

def update_image(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST' and request.FILES.get('image'):
        product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Image updated successfully')
    return redirect('excel_to_db:index')

def process_excel(file_path):
    try:
        df = pd.read_excel(file_path, skiprows=2, header=0)

        df = df.rename(columns={
            'Unnamed: 1': 'unique_model_code',
            'Unnamed: 2': 'product_name',
            'Unnamed: 4': 'specification',
            'USD': 'price'
        })

        workbook = load_workbook(file_path)
        sheet = workbook.active
        image_loader = SheetImageLoader(sheet)
        skipped_rows = 0
        processed_rows = 0
        i = 4  # Starting row for images

        for _, row in df.iterrows():
            try:
                if pd.isna(row['unique_model_code']) or str(row['unique_model_code']).strip() == '':
                    logger.warning(f"Skipping row with invalid unique_model_code: {row}")
                    skipped_rows += 1
                    i += 1
                    continue

                try:
                    image = image_loader.get(f"D{i}")
                except:
                    logger.warning(f"No image found for row {i}, skipping image")
                    image = None

                i += 1

                file = None
                if image:
                    path = f"./static/temp_image.{image.format}"
                    image.save(path)
                    with open(path, "rb") as x:
                        file = x.read()
                    os.remove(path)  # Clean up the temporary file

                product = Product(
                    unique_model_code=str(row['unique_model_code']),
                    product_name=str(row['product_name']),
                    specification=str(row['specification']),
                    price=float(row['price']) if pd.notnull(row['price']) else 0.0,
                )
                if file:
                    product.image.put(file)

                product.save()
                processed_rows += 1

            except Exception as e:
                logger.error(f"Error processing row: {row}")
                logger.error(f"Error details: {str(e)}")
                skipped_rows += 1

        logger.info(f'Excel file processed successfully. Processed {processed_rows} rows, skipped {skipped_rows} rows.')
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise