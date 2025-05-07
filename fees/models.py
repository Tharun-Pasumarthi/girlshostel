from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Fee(models.Model):
    TYPE_CHOICES = [
        ('HOSTEL', 'Hostel Fee'),
        ('MESS', 'Mess Fee'),
        ('MAINTENANCE', 'Maintenance Fee'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fees')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.get_type_display()} - {self.student.get_full_name()}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('CASH', 'Cash'),
        ('ONLINE', 'Online'),
        ('CHEQUE', 'Cheque'),
        ('OTHER', 'Other'),
    ]
    
    fee = models.ForeignKey(Fee, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_created')
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Payment for {self.fee} - {self.amount}"
    
    def save(self, *args, **kwargs):
        # Update fee status when payment is made
        if not self.pk:  # Only on creation
            self.fee.status = 'PAID'
            self.fee.save()
        super().save(*args, **kwargs) 