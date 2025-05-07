from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from .models import Menu, MealFeedback, SpecialMealRequest, MessLeave

@login_required
def menu_list(request):
    """Display the weekly/monthly menu."""
    today = timezone.now().date()
    menus = Menu.objects.filter(date__gte=today).order_by('date', 'meal_type')
    
    context = {
        'menus': menus,
        'today': today,
    }
    return render(request, 'mess/menu_list.html', context)

@login_required
def menu_detail(request, menu_id):
    """Display detailed menu information and feedback."""
    menu = get_object_or_404(Menu, id=menu_id)
    feedback = MealFeedback.objects.filter(menu=menu)
    avg_rating = feedback.aggregate(Avg('rating'))['rating__avg'] or 0
    
    context = {
        'menu': menu,
        'feedback': feedback,
        'avg_rating': round(avg_rating, 1),
    }
    return render(request, 'mess/menu_detail.html', context)

@login_required
def submit_feedback(request, menu_id):
    """Submit feedback for a meal."""
    menu = get_object_or_404(Menu, id=menu_id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        feedback, created = MealFeedback.objects.get_or_create(
            student=request.user,
            menu=menu,
            defaults={
                'rating': rating,
                'comment': comment
            }
        )
        
        if not created:
            feedback.rating = rating
            feedback.comment = comment
            feedback.save()
        
        messages.success(request, 'Thank you for your feedback!')
        return redirect('mess:menu_detail', menu_id=menu.id)
    
    return render(request, 'mess/submit_feedback.html', {'menu': menu})

@login_required
def special_meal_request(request):
    """Submit a special meal request."""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        dietary_requirements = request.POST.get('dietary_requirements')
        
        SpecialMealRequest.objects.create(
            student=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            dietary_requirements=dietary_requirements
        )
        
        messages.success(request, 'Special meal request submitted successfully!')
        return redirect('mess:request_list')
    
    return render(request, 'mess/special_meal_request.html')

@login_required
def request_list(request):
    """List all special meal requests."""
    if request.user.role in ['ADMIN', 'WARDEN']:
        requests = SpecialMealRequest.objects.all().order_by('-created_at')
    else:
        requests = SpecialMealRequest.objects.filter(student=request.user).order_by('-created_at')
    
    return render(request, 'mess/request_list.html', {'requests': requests})

@login_required
def mess_leave_request(request):
    """Submit a mess leave request."""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        MessLeave.objects.create(
            student=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        
        messages.success(request, 'Mess leave request submitted successfully!')
        return redirect('mess:leave_list')
    
    return render(request, 'mess/mess_leave_request.html')

@login_required
def leave_list(request):
    """List all mess leave requests."""
    if request.user.role in ['ADMIN', 'WARDEN']:
        leaves = MessLeave.objects.all().order_by('-created_at')
    else:
        leaves = MessLeave.objects.filter(student=request.user).order_by('-created_at')
    
    return render(request, 'mess/leave_list.html', {'leaves': leaves})

@login_required
def approve_request(request, request_id):
    """Approve or reject a special meal request."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to approve requests.')
        return redirect('mess:request_list')
    
    meal_request = get_object_or_404(SpecialMealRequest, id=request_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            meal_request.status = 'APPROVED' if action == 'approve' else 'REJECTED'
            meal_request.approved_by = request.user
            meal_request.save()
            
            messages.success(request, f'Request {action}d successfully!')
    
    return redirect('mess:request_list')

@login_required
def approve_leave(request, leave_id):
    """Approve or reject a mess leave request."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to approve leaves.')
        return redirect('mess:leave_list')
    
    leave = get_object_or_404(MessLeave, id=leave_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ['approve', 'reject']:
            leave.status = 'APPROVED' if action == 'approve' else 'REJECTED'
            leave.approved_by = request.user
            leave.save()
            
            messages.success(request, f'Leave request {action}d successfully!')
    
    return redirect('mess:leave_list')
