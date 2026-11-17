from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from cars.models import Car
from showrooms.models import Showroom
from .models import Report
from .forms import ReportForm


@login_required
def report_car(request, car_id):
    """Report a car listing"""
    car = get_object_or_404(Car, pk=car_id)
    
    # Can't report your own car
    if car.seller == request.user:
        messages.warning(request, 'You cannot report your own car.')
        return redirect('cars:detail', pk=car.id)
    
    # Check if already reported
    existing_report = Report.objects.filter(
        reporter=request.user,
        reported_car=car,
        status=Report.PENDING
    ).exists()
    
    if existing_report:
        messages.warning(request, 'You have already reported this car.')
        return redirect('cars:detail', pk=car.id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.report_type = Report.CAR
            report.reported_car = car
            report.save()
            
            messages.success(request, '✅ Thank you for your report. Our team will review it shortly.')
            return redirect('cars:detail', pk=car.id)
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'car': car,
        'report_type': 'car',
        'page_title': f'Report {car.title} - SWAT AUTO'
    }
    return render(request, 'reports/report_form.html', context)


@login_required
def report_showroom(request, showroom_id):
    """Report a showroom"""
    showroom = get_object_or_404(Showroom, pk=showroom_id)
    
    if showroom.owner == request.user:
        messages.warning(request, 'You cannot report your own showroom.')
        return redirect('showrooms:detail', slug=showroom.slug)
    
    existing_report = Report.objects.filter(
        reporter=request.user,
        reported_showroom=showroom,
        status=Report.PENDING
    ).exists()
    
    if existing_report:
        messages.warning(request, 'You have already reported this showroom.')
        return redirect('showrooms:detail', slug=showroom.slug)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.report_type = Report.SHOWROOM
            report.reported_showroom = showroom
            report.save()
            
            messages.success(request, '✅ Thank you for your report. Our team will review it shortly.')
            return redirect('showrooms:detail', slug=showroom.slug)
    else:
        form = ReportForm()
    
    context = {
        'form': form,
        'showroom': showroom,
        'report_type': 'showroom',
        'page_title': f'Report {showroom.name} - SWAT AUTO'
    }
    return render(request, 'reports/report_form.html', context)


@login_required
def my_reports(request):
    """Display user's submitted reports"""
    reports = Report.objects.filter(reporter=request.user).order_by('-created_at')
    
    # Counts
    pending = reports.filter(status=Report.PENDING).count()
    resolved = reports.filter(status=Report.RESOLVED).count()
    
    # Pagination
    paginator = Paginator(reports, 10)
    page = request.GET.get('page', 1)
    reports_page = paginator.get_page(page)
    
    context = {
        'reports': reports_page,
        'pending': pending,
        'resolved': resolved,
        'total': reports.count(),
        'page_title': 'My Reports - SWAT AUTO'
    }
    return render(request, 'reports/my_reports.html', context)