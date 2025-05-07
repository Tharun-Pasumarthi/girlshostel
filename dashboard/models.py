from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class Report(models.Model):
    """Generated reports for various aspects of the hostel."""
    TYPE_CHOICES = [
        ('ATTENDANCE', 'Attendance Report'),
        ('FEES', 'Fees Report'),
        ('COMPLAINTS', 'Complaints Report'),
        ('MAINTENANCE', 'Maintenance Report'),
        ('BOOKINGS', 'Facility Bookings Report'),
        ('CUSTOM', 'Custom Report'),
    ]
    
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"

class DashboardWidget(models.Model):
    """Customizable widgets for the dashboard."""
    TYPE_CHOICES = [
        ('STATS', 'Statistics'),
        ('CHART', 'Chart'),
        ('TABLE', 'Table'),
        ('LIST', 'List'),
    ]
    
    title = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    data_source = models.CharField(max_length=100)  # e.g., 'attendance', 'fees', etc.
    configuration = models.JSONField(default=dict)  # Store widget-specific settings
    position = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.title} ({self.get_widget_type_display()})"

class NotificationPreference(models.Model):
    """User preferences for dashboard notifications."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    notification_types = models.JSONField(default=dict)  # Store enabled notification types
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preferences - {self.user.get_full_name()}"
