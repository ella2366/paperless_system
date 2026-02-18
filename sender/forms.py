from django import forms
from django.contrib.auth.models import Group, User
from .models import Document, Department # Siguraduhing imported ang Department

class DocumentForm(forms.ModelForm):
    # Dito natin kukunin ang listahan mula sa Groups
    department_group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Target Department",
        empty_label="Select Department",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Document
        fields = ['title', 'receiver', 'file'] # Tinanggal muna natin ang 'department' dito para hindi mag-error