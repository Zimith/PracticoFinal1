from django.contrib import admin
from .models import Venta, ItemVenta


class ItemVentaInline(admin.TabularInline):
    model = ItemVenta
    readonly_fields = ('subtotal',)
    extra = 0


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'cliente', 'fecha', 'total')
    inlines = [ItemVentaInline]


@admin.register(ItemVenta)
class ItemVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal')
from django.contrib import admin

# Register your models here.
