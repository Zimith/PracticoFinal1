from django import forms
from django.forms import inlineformset_factory

from .models import Venta, ItemVenta
from productos.models import Producto


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente']


class ItemVentaForm(forms.ModelForm):
    class Meta:
        model = ItemVenta
        # remove precio_unitario from editable fields: price will be taken from Producto.precio
        fields = ['producto', 'cantidad']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally limit producto choices to active/available products
        self.fields['producto'].queryset = Producto.objects.all()
        # show nicer widgets
        self.fields['cantidad'].widget.attrs.update({'min': '1', 'class': 'form-control'})
        self.fields['producto'].widget.attrs.update({'class': 'form-select'})


ItemVentaFormSet = inlineformset_factory(
    Venta,
    ItemVenta,
    form=ItemVentaForm,
    extra=1,
    can_delete=True,
)
