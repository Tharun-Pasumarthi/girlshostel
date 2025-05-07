from django import forms
from .models import Report, DashboardWidget, NotificationPreference

class ReportForm(forms.ModelForm):
    """Form for generating reports."""
    class Meta:
        model = Report
        fields = ['title', 'report_type', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")
        
        return cleaned_data

class WidgetForm(forms.ModelForm):
    """Form for creating and editing dashboard widgets."""
    class Meta:
        model = DashboardWidget
        fields = ['title', 'widget_type', 'data_source', 'configuration', 'position', 'is_active']
        widgets = {
            'configuration': forms.JSONField(),
        }
    
    def clean_configuration(self):
        configuration = self.cleaned_data.get('configuration')
        if not isinstance(configuration, dict):
            raise forms.ValidationError("Configuration must be a valid JSON object.")
        return configuration

class NotificationPreferenceForm(forms.ModelForm):
    """Form for managing notification preferences."""
    class Meta:
        model = NotificationPreference
        fields = ['email_notifications', 'push_notifications', 'notification_types']
        widgets = {
            'notification_types': forms.JSONField(),
        }
    
    def clean_notification_types(self):
        notification_types = self.cleaned_data.get('notification_types')
        if not isinstance(notification_types, dict):
            raise forms.ValidationError("Notification types must be a valid JSON object.")
        return notification_types 