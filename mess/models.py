from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Menu(models.Model):
    """Weekly/Monthly food menu."""
    DAY_CHOICES = [
        ('MON', 'Monday'),
        ('TUE', 'Tuesday'),
        ('WED', 'Wednesday'),
        ('THU', 'Thursday'),
        ('FRI', 'Friday'),
        ('SAT', 'Saturday'),
        ('SUN', 'Sunday'),
    ]
    
    MEAL_CHOICES = [
        ('BREAKFAST', 'Breakfast'),
        ('LUNCH', 'Lunch'),
        ('DINNER', 'Dinner'),
    ]
    
    day = models.CharField(max_length=3, choices=DAY_CHOICES, default='MON')
    meal_type = models.CharField(max_length=10, choices=MEAL_CHOICES)
    date = models.DateField()
    items = models.TextField(help_text="List of food items for this meal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['day', 'meal_type', 'date']
        ordering = ['date', 'meal_type']
    
    def __str__(self):
        return f"{self.get_day_display()} - {self.get_meal_type_display()} ({self.date})"

class MealFeedback(models.Model):
    """Student feedback for meals."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['student', 'menu']
    
    def __str__(self):
        return f"Feedback by {self.student.get_full_name()} for {self.menu}"

class SpecialMealRequest(models.Model):
    """Special meal requests for dietary/religious requirements."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(help_text="Reason for special meal request")
    dietary_requirements = models.TextField(help_text="Specific dietary requirements", default="None")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_meal_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Special meal request by {self.student.get_full_name()}"

class MessLeave(models.Model):
    """Mess leave requests for rebate."""
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_mess_leaves'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Mess leave request by {self.student.get_full_name()}"

class MessBill(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mess_bills')
    month = models.DateField()  # First day of the month
    total_days = models.IntegerField()
    days_present = models.IntegerField()
    days_absent = models.IntegerField()
    per_day_rate = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, related_name='mess_bills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('student', 'month')
    
    def __str__(self):
        return f"Mess Bill - {self.student.get_full_name()} - {self.month.strftime('%B %Y')}"
