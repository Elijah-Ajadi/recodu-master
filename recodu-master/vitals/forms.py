from django import forms
from .models import VitalsRecord


class VitalsForm(forms.ModelForm):
    class Meta:
        model = VitalsRecord
        fields = ["patient", "systolic", "diastolic", "pulse", "temperature", "glucose_type", "glucose_value", "notes", "medications"]
        widgets = {
            "patient": forms.HiddenInput(),
            "systolic": forms.NumberInput(attrs={"class": "form-input", "tabindex": "1", "min": "60", "max": "250", "data-threshold-normal-max": "120", "data-threshold-warning-max": "139", "data-threshold-danger-min": "140"}),
            "diastolic": forms.NumberInput(attrs={"class": "form-input", "tabindex": "2", "min": "40", "max": "180", "data-threshold-normal-max": "80", "data-threshold-warning-max": "89", "data-threshold-danger-min": "90"}),
            "pulse": forms.NumberInput(attrs={"class": "form-input", "tabindex": "3", "min": "30", "max": "220", "data-threshold-normal-min": "60", "data-threshold-normal-max": "100", "data-threshold-warning-max": "120"}),
            "temperature": forms.NumberInput(attrs={"class": "form-input", "tabindex": "4", "step": "0.1", "min": "30.0", "max": "45.0", "data-threshold-normal-min": "36.1", "data-threshold-normal-max": "37.2", "data-threshold-danger-min": "38.0"}),
            "glucose_type": forms.RadioSelect(attrs={"class": "glucose-toggle"}),
            "glucose_value": forms.NumberInput(attrs={"class": "form-input", "tabindex": "6", "step": "0.1", "min": "1.0", "max": "40.0"}),
            "notes": forms.Textarea(attrs={"class": "form-input", "tabindex": "7", "rows": "3"}),
            "medications": forms.Textarea(attrs={"class": "form-input", "tabindex": "8", "rows": "2"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in ["systolic", "diastolic", "pulse", "temperature", "glucose_value"]:
            self.fields[field].required = False
