from django.contrib import admin
from .models import Producto
# Register your models here.
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'sku', 'precio', 'stock', 'necesita_reposicion']
    list_filter = ['stock']
    search_fields = ['nombre']