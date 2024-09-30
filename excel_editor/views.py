from django.shortcuts import render

# Create your views here.
import pandas as pd
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .forms import ExcelUploadForm
from .models import ExcelData

def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            df = pd.read_excel(excel_file)
            json_data = df.to_json(orient='records')
            return render(request, 'excel_editor/edit_data.html', {'data': json_data})
    else:
        form = ExcelUploadForm()
    return render(request, 'excel_editor/upload.html', {'form': form})

def save_data(request):
    if request.method == 'POST':
        data = json.loads(request.POST.get('data'))
        excel_data = ExcelData(data=data)
        excel_data.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'})