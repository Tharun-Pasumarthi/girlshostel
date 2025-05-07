from django import forms
from .models import Facility, FacilityBooking, MaintenanceRequest
from django.utils import timezone

class FacilityForm(forms.ModelForm):
    """Form for adding/editing facilities."""
    class Meta:
        model = Facility
        fields = ['name', 'category', 'description', 'location', 'capacity', 
                 'is_available', 'operating_hours', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'operating_hours': forms.TextInput(attrs={'placeholder': 'e.g., 9:00 AM - 10:00 PM'}),
        }

class BookingForm(forms.ModelForm):
    """Form for booking facilities."""
    class Meta:
        model = FacilityBooking
        fields = ['booking_date', 'start_time', 'end_time', 'purpose']
        widgets = {
            'booking_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        booking_date = cleaned_data.get('booking_date')
        
        if start_time and end_time and booking_date:
            if start_time >= end_time:
                raise forms.ValidationError('End time must be after start time.')
            
            if booking_date < timezone.now().date():
                raise forms.ValidationError('Cannot book for past dates.')
        
        return cleaned_data

class MaintenanceRequestForm(forms.ModelForm):
    """Form for reporting maintenance issues."""
    class Meta:
        model = MaintenanceRequest
        fields = ['title', 'description', 'priority']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        } 