from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from products.models import Product
from blog.models import BlogPost


# ==========================
# Static Pages
# ==========================
class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "monthly"

    def items(self):
        return [
            "home",
            "products",
            "blog",
            "pricing",
            "nutrition_guides",
            "contact",
            "terms",
        ]

    def location(self, item):
        return reverse(item)


# ==========================
# Products
# ==========================
class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Product.objects.filter(is_available=True)

    def location(self, obj):
        return reverse("product_detail", args=[obj.id])

    def lastmod(self, obj):
        return obj.updated_at


# ==========================
# Blog Posts
# ==========================
class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return BlogPost.objects.all()

    def location(self, obj):
        return f"/blog/{obj.slug}/"
