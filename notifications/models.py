from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Notification(models.Model):
    class Type(models.TextChoices):
        PAYMENT = 'PAYMENT', _('Payment')
        LEAVE = 'LEAVE', _('Leave')
        COMPLAINT = 'COMPLAINT', _('Complaint')
        MESS = 'MESS', _('Mess')
        ROOM = 'ROOM', _('Room')
        ANNOUNCEMENT = 'ANNOUNCEMENT', _('Announcement')
        OTHER = 'OTHER', _('Other')
    
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=Type.choices)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Notification - {self.title} ({self.get_type_display()})"

class Announcement(models.Model):
    class Type(models.TextChoices):
        GENERAL = 'GENERAL', _('General')
        EMERGENCY = 'EMERGENCY', _('Emergency')
        MAINTENANCE = 'MAINTENANCE', _('Maintenance')
        EVENT = 'EVENT', _('Event')
        OTHER = 'OTHER', _('Other')
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    type = models.CharField(max_length=20, choices=Type.choices)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Announcement - {self.title} ({self.get_type_display()})"

class AnnouncementAttachment(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='announcement_attachments/')
    description = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Attachment - {self.announcement.title}"

class BroadcastMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipients = models.ManyToManyField(User, related_name='received_messages')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message - {self.subject}"

class MessageRecipient(models.Model):
    message = models.ForeignKey(BroadcastMessage, on_delete=models.CASCADE, related_name='recipient_status')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_status')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('message', 'recipient')
    
    def __str__(self):
        return f"Message Status - {self.recipient.get_full_name()}"
