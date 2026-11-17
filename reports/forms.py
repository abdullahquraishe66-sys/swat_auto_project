from django import forms
from .models import Report


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'reason': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Please provide additional details about your report...'
            }),
        }
        labels = {
            'reason': 'Reason for Report',
            'description': 'Additional Details (Optional)'
        }
    
    def clean_description(self):
        description = self.cleaned_data.get('description', '').strip()
        # If reason is "Other", description is required
        reason = self.cleaned_data.get('reason')
        if reason == 'other' and not description:
            raise forms.ValidationError('Please provide details when selecting "Other".')
        return description