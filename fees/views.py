from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from accounts.models import User
from .models import Fee, Payment

@login_required
def fee_list_view(request):
    """List all fees."""
    if request.user.role == 'STUDENT':
        fees = request.user.fees.all()
    else:
        fees = Fee.objects.all()
    
    context = {
        'fees': fees,
    }
    return render(request, 'fees/fee_list.html', context)

@login_required
def fee_create_view(request):
    """Create a new fee record."""
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        student_id = request.POST.get('student')
        type = request.POST.get('type')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        description = request.POST.get('description')
        
        student = get_object_or_404(User, id=student_id, role='STUDENT')
        
        fee = Fee.objects.create(
            student=student,
            type=type,
            amount=amount,
            due_date=due_date,
            description=description,
        )
        
        messages.success(request, 'Fee record created successfully!')
        return redirect('fees:fee_detail', fee_id=fee.id)
    
    students = User.objects.filter(role='STUDENT')
    context = {
        'students': students,
    }
    return render(request, 'fees/fee_form.html', context)

@login_required
def fee_detail_view(request, fee_id):
    """View fee details."""
    fee = get_object_or_404(Fee, id=fee_id)
    
    # Check if user has permission to view this fee
    if request.user.role not in ['ADMIN', 'WARDEN'] and fee.student != request.user:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    context = {
        'fee': fee,
        'payments': fee.payments.all(),
    }
    return render(request, 'fees/fee_detail.html', context)

@login_required
def fee_edit_view(request, fee_id):
    """Edit a fee record."""
    fee = get_object_or_404(Fee, id=fee_id)
    
    # Check if user has permission to edit this fee
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        fee.type = request.POST.get('type')
        fee.amount = request.POST.get('amount')
        fee.due_date = request.POST.get('due_date')
        fee.description = request.POST.get('description')
        fee.save()
        
        messages.success(request, 'Fee record updated successfully!')
        return redirect('fees:fee_detail', fee_id=fee.id)
    
    context = {
        'fee': fee,
    }
    return render(request, 'fees/fee_form.html', context)

@login_required
def fee_delete_view(request, fee_id):
    """Delete a fee record."""
    fee = get_object_or_404(Fee, id=fee_id)
    
    # Check if user has permission to delete this fee
    if request.user.role not in ['ADMIN', 'WARDEN']:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee record deleted successfully!')
        return redirect('fees:fee_list')
    
    context = {
        'fee': fee,
    }
    return render(request, 'fees/fee_confirm_delete.html', context)

@login_required
def fee_payment_view(request, fee_id):
    """Process a fee payment."""
    fee = get_object_or_404(Fee, id=fee_id)
    
    # Check if user has permission to make this payment
    if request.user.role not in ['ADMIN', 'WARDEN'] and fee.student != request.user:
        messages.error(request, 'You do not have permission to view this page.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        amount = request.POST.get('amount')
        payment_method = request.POST.get('payment_method')
        transaction_id = request.POST.get('transaction_id')
        notes = request.POST.get('notes')
        
        payment = Payment.objects.create(
            fee=fee,
            amount=amount,
            payment_method=payment_method,
            transaction_id=transaction_id,
            notes=notes,
            created_by=request.user,
        )
        
        messages.success(request, 'Payment processed successfully!')
        return redirect('fees:fee_detail', fee_id=fee.id)
    
    context = {
        'fee': fee,
    }
    return render(request, 'fees/fee_payment.html', context)

@login_required
def payment_history_view(request):
    """View payment history."""
    if request.user.role == 'STUDENT':
        payments = Payment.objects.filter(fee__student=request.user)
    else:
        payments = Payment.objects.all()
    
    context = {
        'payments': payments,
    }
    return render(request, 'fees/payment_history.html', context) 