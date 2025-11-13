from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventario.mixins import FriendlyPermissionRequiredMixin
from django.db import transaction
from django.db.models import Q, Sum
from django.contrib import messages

from .models import Venta, ItemVenta
from productos.models import Producto
from .forms import VentaForm, ItemVentaFormSet
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

try:
    # optional import — available once we installed the package
    from weasyprint import HTML
except Exception:
    HTML = None


class VentaListView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, ListView):
    permission_required = 'ventas.view_venta'
    model = Venta
    template_name = 'ventas/venta_list.html'
    context_object_name = 'ventas'
    paginate_by = 5

    def get_queryset(self):
        """Filter by date range (dd/mm/yyyy) and by cliente id from GET params.

        GET params supported:
        - desde: start date in dd/mm/YYYY
        - hasta: end date in dd/mm/YYYY
        - cliente: Cliente id
        """
        qs = super().get_queryset()
        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')
        cliente = self.request.GET.get('cliente')

        from datetime import datetime
        from django.contrib import messages

        # filter by cliente id or fuzzy match if provided
        if cliente:
            # cliente may be: an id, a string like '123 - Apellido, Nombre (...)', or a name fragment
            from clientes.models import Cliente as ClienteModel
            import re

            cid = None
            # plain numeric id
            if cliente.isdigit():
                cid = int(cliente)
            else:
                m = re.match(r"^(\d+)\s*-\s*", cliente)
                if m:
                    try:
                        cid = int(m.group(1))
                    except (ValueError, TypeError):
                        cid = None

            if cid:
                qs = qs.filter(cliente_id=cid)
            else:
                # try to find matching clients by name/apellido/documento
                candidates = ClienteModel.objects.filter(
                    Q(nombre__icontains=cliente) | Q(apellido__icontains=cliente) | Q(documento__icontains=cliente)
                )
                if candidates.count() == 1:
                    qs = qs.filter(cliente_id=candidates.first().pk)
                elif candidates.count() == 0:
                    messages.error(self.request, 'Cliente no encontrado')
                else:
                    messages.error(self.request, 'Varios clientes coinciden; seleccione el correcto de la lista')

        # filter by desde/hasta dates
        if desde:
            try:
                d = datetime.strptime(desde, '%d/%m/%Y').date()
                qs = qs.filter(fecha__date__gte=d)
            except ValueError:
                messages.error(self.request, 'Formato de fecha "desde" inválido. Use dd/mm/aaaa')

        if hasta:
            try:
                h = datetime.strptime(hasta, '%d/%m/%Y').date()
                qs = qs.filter(fecha__date__lte=h)
            except ValueError:
                messages.error(self.request, 'Formato de fecha "hasta" inválido. Use dd/mm/aaaa')

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # provide clients for the filter select and current filter values
        from clientes.models import Cliente

        context['clientes'] = Cliente.objects.all()
        context['filter_desde'] = self.request.GET.get('desde', '')
        context['filter_hasta'] = self.request.GET.get('hasta', '')
        context['filter_cliente'] = self.request.GET.get('cliente', '')
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')
        context['querystring'] = params.urlencode()
        return context


class VentasPorDiaJSONView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, View):
    """Return JSON with sales totals grouped by day for the chart.

    Response format: [{"date": "YYYY-MM-DD", "total": 123.45}, ...]
    """
    permission_required = 'ventas.view_venta'

    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.db.models import DateField, DateTimeField
        from django.db.models.functions import TruncDate

        qs = Venta.objects.all()

        # Apply same filters as list view if present
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        cliente = request.GET.get('cliente')

        from datetime import datetime
        if cliente:
            if cliente.isdigit():
                qs = qs.filter(cliente_id=int(cliente))

        if desde:
            try:
                d = datetime.strptime(desde, '%d/%m/%Y').date()
                qs = qs.filter(fecha__date__gte=d)
            except ValueError:
                pass
        if hasta:
            try:
                h = datetime.strptime(hasta, '%d/%m/%Y').date()
                qs = qs.filter(fecha__date__lte=h)
            except ValueError:
                pass

        data = (
            qs.annotate(day=TruncDate('fecha'))
            .values('day')
            .order_by('day')
            .annotate(total=Sum('total'))
        )

        # Build response list
        out = []
        for row in data:
            day = row['day']
            total = row['total'] or 0
            out.append({'date': day.isoformat(), 'total': float(total)})

        return JsonResponse(out, safe=False)


class VentasPorProductoJSONView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, View):
    """Return JSON with sales totals grouped by product.

    Response format: [{"product": "Nombre producto", "total": 123.45}, ...]
    """
    permission_required = 'ventas.view_venta'

    def get(self, request, *args, **kwargs):
        from django.http import JsonResponse
        from django.db.models import Sum

        qs = ItemVenta.objects.select_related('producto').all()

        # Apply optional filters from the list view (fecha range, cliente)
        desde = request.GET.get('desde')
        hasta = request.GET.get('hasta')
        cliente = request.GET.get('cliente')

        from datetime import datetime
        if cliente:
            if cliente.isdigit():
                qs = qs.filter(venta__cliente_id=int(cliente))

        if desde:
            try:
                d = datetime.strptime(desde, '%d/%m/%Y').date()
                qs = qs.filter(venta__fecha__date__gte=d)
            except ValueError:
                pass
        if hasta:
            try:
                h = datetime.strptime(hasta, '%d/%m/%Y').date()
                qs = qs.filter(venta__fecha__date__lte=h)
            except ValueError:
                pass

        data = (
            qs.values('producto__id', 'producto__nombre')
            .annotate(total=Sum('subtotal'))
            .order_by('-total')
        )

        out = []
        for row in data:
            name = row.get('producto__nombre') or '—'
            total = row.get('total') or 0
            out.append({'product': name, 'total': float(total)})

        return JsonResponse(out, safe=False)


class VentaDetailView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, DetailView):
    permission_required = 'ventas.view_venta'
    model = Venta
    template_name = 'ventas/venta_detail.html'
    context_object_name = 'venta'


class VentaPDFView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, View):
    permission_required = 'ventas.view_venta'

    def get(self, request, pk, *args, **kwargs):
        venta = get_object_or_404(Venta, pk=pk)

        if HTML is None:
            return HttpResponse('WeasyPrint no está instalado en el sistema.', status=500)

        html_string = render_to_string('ventas/venta_pdf.html', {'venta': venta, 'request': request})
        # base_url ensures static files (if referenced) are resolved
        pdf = HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename=venta_{venta.codigo}.pdf'
        return response


class VentaCreateView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, View):
    permission_required = 'ventas.add_venta'
    template_name = 'ventas/venta_form.html'

    def get(self, request, *args, **kwargs):
        venta_form = VentaForm()
        formset = ItemVentaFormSet()
        return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset})

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
                # re-render with errors
                return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset})

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

        # invalid - re-render with forms (no frontend price JS required)
        return render(request, self.template_name, {'venta_form': venta_form, 'formset': formset})
