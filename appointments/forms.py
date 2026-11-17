from django import forms
from .models import ViewingRequest
from django.utils import timezone
import datetime

class ViewingRequestForm(forms.ModelForm):
    class Meta:
        model = ViewingRequest
        fields = ['preferred_date', 'preferred_time', 'message']
        widgets = {
            'preferred_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': datetime.date.today().isoformat()
            }),
            'preferred_time': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Any additional information or questions...'
            }),
        }
        labels = {
            'preferred_date': 'Preferred Date',
            'preferred_time': 'Preferred Time',
            'message': 'Message (Optional)'
        }
    
    def clean_preferred_date(self):
        date = self.cleaned_data.get('preferred_date')
        if date < datetime.date.today():
            raise forms.ValidationError('Please select a future date.')
        return date

class ResponseForm(forms.Form):
    response_message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a message for the buyer...'
        }),
        required=False,
        label='Response Message (Optional)'
    )