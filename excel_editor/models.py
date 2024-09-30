from django.db import models

# Create your models here.
from djongo import models

class ExcelData(models.Model):
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Excel Data {self.id}"