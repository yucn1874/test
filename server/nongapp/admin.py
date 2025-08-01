from django.contrib import admin
from .models import ProductPrice


@admin.register(ProductPrice)
class ProductPriceAdmin(admin.ModelAdmin):
    list_display = ('data', 'category', 'variety', 'price', 'area', 'unit')
    list_filter = ('variety', 'area', 'category')
    search_fields = ('variety', 'area')



