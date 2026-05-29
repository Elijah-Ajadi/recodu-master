from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "phone", "gender", "age_range", "blood_group", "genotype", "known_conditions"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "tabindex": "1"}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "tabindex": "2"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "tabindex": "3"}),
            "gender": forms.Select(attrs={"class": "form-input", "tabindex": "4"}),
            "age_range": forms.Select(attrs={"class": "form-input", "tabindex": "5"}),
            "blood_group": forms.Select(attrs={"class": "form-input", "tabindex": "6"}),
            "genotype": forms.Select(attrs={"class": "form-input", "tabindex": "7"}),
            "known_conditions": forms.Textarea(attrs={"class": "form-input", "rows": "3"}),
        }


class PatientRegistrationForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["first_name", "last_name", "phone", "gender", "age_range"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-input", "tabindex": "1", "autofocus": True}),
            "last_name": forms.TextInput(attrs={"class": "form-input", "tabindex": "2"}),
            "phone": forms.TextInput(attrs={"class": "form-input", "tabindex": "3"}),
            "gender": forms.Select(attrs={"class": "form-input", "tabindex": "4"}),
            "age_range": forms.Select(attrs={"class": "form-input", "tabindex": "5"}),
        }
