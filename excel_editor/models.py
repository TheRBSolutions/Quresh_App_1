from django.db import models
from bson.binary import Binary

class ExcelData(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Excel Data {self.id}"

class ExcelImage(models.Model):
    excel_data = models.ForeignKey(ExcelData, related_name='images', on_delete=models.CASCADE)
    number = models.IntegerField()
    image = models.BinaryField()
    information = models.TextField(default='')  # Added default value
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Added default value

    class Meta:
        ordering = ['number']

    def set_image(self, image_data):
        self.image = Binary(image_data)

    def get_image(self):
        return self.image

    def __str__(self):
        return f"Excel Image {self.number} for Excel Data {self.excel_data.id}"