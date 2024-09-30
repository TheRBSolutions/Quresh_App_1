from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['unique_model_code', 'product_name', 'specification', 'price', 'image']

class ExcelUploadForm(forms.Form):
    file = forms.FileField(label='Excel File')