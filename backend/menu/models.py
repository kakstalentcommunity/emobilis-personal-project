from django.db import models
class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    sort_order = models.PositiveIntegerField(default=0)
    class Meta: ordering = ['sort_order','name']
    def __str__(self): return self.name
class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    cost_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    image_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    prep_minutes = models.PositiveIntegerField(default=10)
    def __str__(self): return self.name
