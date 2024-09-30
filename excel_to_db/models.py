from djongo import models

class Product(models.Model):
    _id = models.ObjectIdField()
    no = models.IntegerField(unique=True)
    unique_model_code = models.CharField(max_length=50, unique=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    product_name = models.CharField(max_length=100)
    specification = models.TextField(blank=True)
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.no:
            last_product = Product.objects.order_by('-no').first()
            self.no = (last_product.no + 1) if last_product else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.product_name

    class Meta:
        db_table = 'products'