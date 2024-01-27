from django import forms
from .models import Party

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = '__all__'  # You can also specify the fields you want to include instead of '__all__'