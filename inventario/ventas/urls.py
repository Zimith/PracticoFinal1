from django.urls import path
from . import views

app_name = 'ventas'

urlpatterns = [
    path('', views.VentaListView.as_view(), name='venta_list'),
    path('por-dia/', views.VentasPorDiaJSONView.as_view(), name='ventas_por_dia'),
    path('por-producto/', views.VentasPorProductoJSONView.as_view(), name='ventas_por_producto'),
    path('nueva/', views.VentaCreateView.as_view(), name='venta_create'),
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
]
