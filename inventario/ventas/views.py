from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventario.mixins import FriendlyPermissionRequiredMixin
from django.db import transaction
from django.contrib import messages

from .models import Venta, ItemVenta
from productos.models import Producto
from .forms import VentaForm, ItemVentaFormSet
import json


class VentaListView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, ListView):
    permission_required = 'ventas.view_venta'
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'


class VentaDetailView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, DetailView):
    permission_required = 'ventas.view_venta'
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'


class VentaCreateView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, View):
    permission_required = 'ventas.add_venta'
    template_name = 'ventas/venta_form.html'

    def get(self, request, *args, **kwargs):
        venta_form = VentaForm()
        formset = ItemVentaFormSet()
        # prepare product price mapping for frontend
        product_prices = {p.pk: str(p.precio) for p in Producto.objects.all()}
        return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset, 'product_prices_json': json.dumps(product_prices)})

    def post(self, request, *args, **kwargs):
        venta_form = VentaForm(request.POST)
        formset = ItemVentaFormSet(request.POST)
        if venta_form.is_valid() and formset.is_valid():
            # Validate stock availability before performing any writes
            invalid = False
            shortages = []
            for item_form in formset:
                if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                    producto = item_form.cleaned_data.get('producto')
                    cantidad = item_form.cleaned_data.get('cantidad')
                    # basic validation
                    if cantidad is None or cantidad <= 0:
                        item_form.add_error('cantidad', 'La cantidad debe ser mayor que 0.')
                        invalid = True
                    elif producto is None:
                        item_form.add_error('producto', 'Seleccione un producto válido.')
                        invalid = True
                    elif cantidad > producto.stock:
                        item_form.add_error('cantidad', f'Sólo hay {producto.stock} unidades disponibles de {producto.nombre}.')
                        shortages.append(f"{producto.nombre}: {producto.stock} disponibles")
                        invalid = True

            if invalid:
                # Add a friendly alert message if there are shortages
                if shortages:
                    messages.error(request, 'Stock insuficiente para: ' + '; '.join(shortages))
                # re-render with errors (include product prices for JS)
                product_prices = {p.pk: str(p.precio) for p in Producto.objects.all()}
                return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset, 'product_prices_json': json.dumps(product_prices)})

            with transaction.atomic():
                venta = venta_form.save(commit=False)
                venta.total = Decimal('0.00')
                venta.save()

                total = Decimal('0.00')
                for item_form in formset:
                    if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                        producto = item_form.cleaned_data['producto']
                        cantidad = item_form.cleaned_data['cantidad']
                        # precio_unitario is taken from the Producto model to avoid client edits
                        precio = producto.precio
                        subtotal = (Decimal(cantidad) * Decimal(precio))

                        item = item_form.save(commit=False)
                        item.venta = venta
                        item.precio_unitario = precio
                        item.subtotal = subtotal
                        item.save()

                        # decrement stock (safe because we validated availability)
                        producto.stock = producto.stock - cantidad
                        producto.save()

                        total += subtotal

                venta.total = total
                venta.save()

                return redirect('ventas:venta_detail', pk=venta.pk)

        # invalid
        return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset})
