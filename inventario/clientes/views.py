from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from inventario.mixins import FriendlyPermissionRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import Cliente
from .forms import ClienteForm

class ClienteListView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, ListView):
    permission_required = 'clientes.view_cliente'
    model = Cliente
    template_name = 'clientes/cliente_list.html'
    context_object_name = 'clientes'
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(documento__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        if 'page' in params:
            params.pop('page')
        context['querystring'] = params.urlencode()
        context['q'] = self.request.GET.get('q', '')
        return context

class ClienteDetailView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, DetailView):
    permission_required = 'clientes.view_cliente'
    model = Cliente
    template_name = 'clientes/cliente_detail.html'
    context_object_name = 'cliente'

class ClienteCreateView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, CreateView):
    permission_required = 'clientes.add_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente creado con éxito')
        return response

class ClienteUpdateView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, UpdateView):
    permission_required = 'clientes.change_cliente'
    model = Cliente
    form_class = ClienteForm
    template_name = 'clientes/cliente_form.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Cliente actualizado con éxito')
        return response

class ClienteDeleteView(LoginRequiredMixin, FriendlyPermissionRequiredMixin, DeleteView):
    permission_required = 'clientes.delete_cliente'
    model = Cliente
    template_name = 'clientes/cliente_confirm_delete.html'
    success_url = reverse_lazy('clientes:cliente_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Cliente eliminado exitosamente')
        return super().delete(request, *args, **kwargs)
