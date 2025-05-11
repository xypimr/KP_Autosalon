from django import forms
from django.forms.models import inlineformset_factory
from .models import Service, ServicePart, Part

ServicePartFormSet = inlineformset_factory(
    Service,
    ServicePart,
    fields=('part', 'quantity'),
    extra=1,
    can_delete=True
)

class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['part_number', 'name', 'cost', 'stock']
        widgets = {
            'part_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите артикул'}),
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите наименование'}),
            'cost':        forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите стоимость'}),
            'stock':       forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Остаток на складе'}),
        }