from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['apellido', 'nombre', 'documento', 'email', 'telefono']
    search_fields = ['apellido', 'nombre', 'documento', 'email']
    list_filter = []
    readonly_fields = ['documento']
