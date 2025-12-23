from django.db import models
from django.urls import reverse
from django.conf import settings

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    images = models.ImageField(upload_to='photos/products', null=True, blank=True)
    stock = models.PositiveIntegerField()
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=True)
    is_digital = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])


class Review(models.Model):
    product = models.ForeignKey(
        Product, related_name="reviews", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    rating = models.IntegerField()
    title = models.CharField(max_length=100)
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.user.username}"
