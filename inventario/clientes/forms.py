from django import forms
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Reset
from .models import Cliente
from productos.crispy import BaseFormHelper

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'documento', 'email', 'telefono', 'direccion']
        widgets = {
            'direccion': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'documento': 'Número de documento',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = BaseFormHelper()
        self.helper.layout = Layout(
            Field('nombre'),
            Field('apellido'),
            Field('documento'),
            Field('email'),
            Field('telefono'),
            Field('direccion'),
            ButtonHolder(
                Submit('submit', 'Guardar', css_class='btn btn-success'),
                Reset('reset', 'Limpiar', css_class='btn btn-outline-secondary')
            )
        )

    def clean_documento(self):
        documento = self.cleaned_data.get('documento')
        if documento:
            qs = Cliente.objects.filter(documento=documento)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Ya existe un cliente con ese número de documento')
        return documento
