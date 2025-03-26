from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q

from .models import Report
from .forms import ReportForm, ReportFilterForm, ReportResponseForm
@login_required
def report_list(request):
    """Vista para ver la lista de reportes."""
    # Los administradores ven todos los reportes, los usuarios solo ven los suyos
    if request.user.is_staff:
        reports = Report.objects.all().order_by('-created_at')
    else:
        reports = Report.objects.filter(user=request.user).order_by('-created_at')
    
    # Aplicar filtros si existen
    filter_form = ReportFilterForm(request.GET)
    
    if filter_form.is_valid():
        # Filtrar por tipo
        if report_type := filter_form.cleaned_data.get('report_type'):
            reports = reports.filter(report_type=report_type)
        
        # Filtrar por importancia
        if importance := filter_form.cleaned_data.get('importance'):
            reports = reports.filter(importance=importance)
        
        # Filtrar por leídos/no leídos
        if filter_form.cleaned_data.get('read'):
            reports = reports.filter(read=False)
        
        # Búsqueda de texto
        if search := filter_form.cleaned_data.get('search'):
            reports = reports.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search)
            )
    
    # Paginación
    paginator = Paginator(reports, 10)  # 10 reportes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reports': page_obj,
        'filter_form': filter_form,
        'page_obj': page_obj,
        'is_paginated': True,
        'paginator': paginator,
        'is_admin': request.user.is_staff
    }
    
    return render(request, 'reports/report_list.html', context)

@login_required
def report_detail(request, pk):
    """Vista para ver un reporte específico."""
    report = get_object_or_404(Report, id=pk)
    
    # Verificar permisos (solo admin o el creador pueden ver)
    if not request.user.is_staff and request.user != report.user:
        return HttpResponseForbidden("No tienes permiso para ver este reporte.")
    
    # Marcar como leído si es admin
    if request.user.is_staff and not report.read:
        report.read = True
        report.save()
    
    # Procesar respuesta si es admin
    if request.user.is_staff and request.method == 'POST':
        response_form = ReportResponseForm(request.POST, instance=report)
        if response_form.is_valid():
            report_response = response_form.save(commit=False)
            report_response.response_by = request.user
            report_response.response_at = timezone.now()
            report_response.save()
            messages.success(request, 'Respuesta enviada correctamente.')
            return redirect('reports:report_detail', pk=report.pk)
    else:
        response_form = ReportResponseForm(instance=report)
    
    context = {
        'report': report,
        'is_admin': request.user.is_staff,
        'response_form': response_form if request.user.is_staff else None
    }
    
    return render(request, 'reports/report_detail.html', context)

@login_required
def create_report(request):
    """Vista para crear un nuevo reporte."""
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            try:
                report = form.save(commit=False)
                report.user = request.user
                report.save()
                
                messages.success(request, 'Reporte enviado exitosamente.')
                return redirect('reports:report_detail', pk=report.pk)
            except Exception as e:
                messages.error(request, f'Error al crear el reporte: {str(e)}')
                print(f"ERROR: {str(e)}")
        else:
            print(f"Errores de formulario: {form.errors}")
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {'form': form})

@login_required
def update_report(request, pk):
    """Vista para actualizar un reporte existente."""
    report = get_object_or_404(Report, pk=pk)
    
    # Solo el creador o un admin pueden editar
    if not request.user.is_staff and request.user != report.user:
        return HttpResponseForbidden("No tienes permiso para editar este reporte.")
    
    # No se puede editar si ya tiene respuesta
    if report.response and not request.user.is_staff:
        messages.warning(request, 'No puedes editar un reporte que ya ha sido respondido.')
        return redirect('reports:report_detail', pk=report.pk)
    
    if request.method == 'POST':
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reporte actualizado exitosamente.')
            return redirect('reports:report_detail', pk=report.pk)
    else:
        form = ReportForm(instance=report)
    
    return render(request, 'reports/report_form.html', {'form': form, 'report': report})

@login_required
def delete_report(request, pk):
    """Vista para eliminar un reporte."""
    report = get_object_or_404(Report, pk=pk)
    
    # Solo el creador o un admin pueden eliminar
    if not request.user.is_staff and request.user != report.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este reporte.")
    
    if request.method == 'POST':
        report.delete()
        messages.success(request, 'Reporte eliminado exitosamente.')
        return redirect('reports:report_list')
    
    return render(request, 'reports/report_confirm_delete.html', {'report': report})

@login_required
def mark_as_read(request, pk):
    """Vista para marcar un reporte como leído."""
    report = get_object_or_404(Report, pk=pk)
    
    # Solo los administradores pueden marcar como leído/no leído
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden marcar reportes como leídos.")
    
    report.read = True
    report.save()
    messages.success(request, 'Reporte marcado como leído.')
    return redirect('reports:report_list')

@login_required
def mark_as_unread(request, pk):
    """Vista para marcar un reporte como no leído."""
    report = get_object_or_404(Report, pk=pk)
    
    # Solo los administradores pueden marcar como leído/no leído
    if not request.user.is_staff:
        return HttpResponseForbidden("Solo los administradores pueden marcar reportes como no leídos.")
    
    report.read = False
    report.save()
    messages.success(request, 'Reporte marcado como no leído.')
    return redirect('reports:report_list')
