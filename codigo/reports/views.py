from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render

from . import _utils, public
from .constants import (CREATE_REPORT_NAME, DELETE_REPORT_NAME,
                        FILTER_FORM_KEY, IS_ADMIN_KEY, IS_PAGINATED_KEY,
                        MARK_READ_NAME, MARK_UNREAD_NAME, PAGE_OBJ_KEY,
                        PAGINATOR_KEY, PAYMENT_KEY, REPORT_CREATED_SUCCESS,
                        REPORT_DELETE_TEMPLATE, REPORT_DELETED_SUCCESS,
                        REPORT_DETAIL_NAME, REPORT_DETAIL_TEMPLATE,
                        REPORT_FORM_TEMPLATE, REPORT_KEY, REPORT_LIST_NAME,
                        REPORT_LIST_TEMPLATE, REPORT_MARKED_READ,
                        REPORT_MARKED_UNREAD, REPORT_UPDATED_SUCCESS,
                        REPORTED_USER_KEY, REPORTS_KEY, RESPONSE_FORM_KEY,
                        RIDE_KEY, UPDATE_REPORT_NAME, get_url_full)
from .forms import ReportFilterForm, ReportForm, ReportResponseForm
from .models import Report


@login_required
def report_list(request):
    """Vista para ver la lista de reportes."""
    # Los administradores ven todos los reportes, los usuarios solo ven los suyos
    if request.user.is_staff:
        reports = Report.objects.all().order_by("-created_at")
    else:
        reports = public.get_user_reports(request.user)

    # Aplicar filtros manualmente
    filter_form = ReportFilterForm(request.GET)

    # Filtro de tipo
    if report_type := request.GET.get("report_type"):
        if report_type:
            reports = reports.filter(report_type=report_type)

    # Filtro de importancia - Aplicación manual
    if importance := request.GET.get("importance"):
        if importance:
            # Filtrar directamente con el valor exacto
            print(f"Aplicando filtro de importancia: '{importance}'")
            reports = reports.filter(importance=importance)

    # Filtro de estado
    if status := request.GET.get("status"):
        if status == "unread":
            reports = reports.filter(read=False)
        elif status == "read":
            reports = reports.filter(read=True)
        elif status == "responded":
            reports = reports.filter(response__isnull=False).exclude(response="")

    # Búsqueda
    if search := request.GET.get("search"):
        reports = reports.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Paginación
    page_obj = _utils.paginate_reports(request, reports)

    context = {
        "reports": page_obj,
        "filter_form": filter_form,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "paginator": page_obj.paginator,
        "is_admin": request.user.is_staff,
    }

    return render(request, REPORT_LIST_TEMPLATE, context)


@login_required
def my_reports(request):
    """Vista para ver los reportes del usuario actual."""
    # Obtener solo los reportes creados por el usuario actual
    reports = public.get_user_reports(request.user)

    # Aplicar filtros manualmente - mismo código que en report_list
    filter_form = ReportFilterForm(request.GET)

    # Filtro de tipo
    if report_type := request.GET.get("report_type"):
        if report_type:
            reports = reports.filter(report_type=report_type)

    # Filtro de importancia - Aplicación manual
    if importance := request.GET.get("importance"):
        if importance:
            # Filtrar directamente con el valor exacto
            print(f"Aplicando filtro de importancia: '{importance}'")
            reports = reports.filter(importance=importance)

    # Filtro de estado
    if status := request.GET.get("status"):
        if status == "unread":
            reports = reports.filter(read=False)
        elif status == "read":
            reports = reports.filter(read=True)
        elif status == "responded":
            reports = reports.filter(response__isnull=False).exclude(response="")

    # Búsqueda
    if search := request.GET.get("search"):
        reports = reports.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )

    # Paginación
    page_obj = _utils.paginate_reports(request, reports)

    context = {
        "reports": page_obj,
        "filter_form": filter_form,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "paginator": page_obj.paginator,
        "is_admin": request.user.is_staff,
        "is_my_reports": True,
    }

    return render(request, REPORT_LIST_TEMPLATE, context)


@login_required
def report_detail(request, pk):
    """Vista para ver un reporte específico."""
    report = _utils.get_report_or_404(pk)

    permission_check = _utils.check_report_view_permission(request, report)
    if permission_check:
        return permission_check

    if request.user.is_staff and not report.read:
        public.mark_report_as_read(report)

    if request.user.is_staff and request.method == "POST":
        response_result = _utils.handle_report_response(request, report)
        if response_result:
            return response_result

    context = _utils.prepare_report_context(report, request.user)

    return render(request, REPORT_DETAIL_TEMPLATE, context)


@login_required
def create_report(request):
    """Vista para crear un nuevo reporte."""
    reported_user, ride, payment, initial_data = _utils.get_related_objects(request)

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            try:
                report = form.save(commit=False)
                report.user = request.user

                if reported_user:
                    report.reported_user = reported_user
                elif ride:
                    report.ride = ride
                elif payment:
                    report.payment = payment

                report.save()

                messages.success(request, REPORT_CREATED_SUCCESS)
                return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)
            except Exception as e:
                messages.error(request, f"Error al crear el reporte: {str(e)}")
                print(f"ERROR: {str(e)}")
        else:
            print(f"Errores de formulario: {form.errors}")
    else:
        form = ReportForm(initial=initial_data)

    context = _utils.prepare_create_report_context(form, reported_user, ride, payment)

    return render(request, REPORT_FORM_TEMPLATE, context)


@login_required
def update_report(request, pk):
    """Vista para actualizar un reporte existente."""
    report = _utils.get_report_or_404(pk)

    permission_check = _utils.check_report_edit_permission(request, report)
    if permission_check:
        return permission_check

    if request.method == "POST":
        form = ReportForm(request.POST, instance=report)
        if form.is_valid():
            form.save()
            messages.success(request, REPORT_UPDATED_SUCCESS)
            return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)
    else:
        form = ReportForm(instance=report)

    return render(request, REPORT_FORM_TEMPLATE, {"form": form, "report": report})


@login_required
def delete_report(request, pk):
    """Vista para eliminar un reporte."""
    report = _utils.get_report_or_404(pk)

    if not public.can_delete_report(request.user, report):
        return HttpResponseForbidden("No tienes permiso para eliminar este reporte.")

    if request.method == "POST":
        report.delete()
        messages.success(request, REPORT_DELETED_SUCCESS)
        return redirect(get_url_full(REPORT_LIST_NAME))

    return render(request, REPORT_DELETE_TEMPLATE, {"report": report})


@login_required
def mark_as_read(request, pk):
    """Vista para marcar un reporte como leído."""
    report = _utils.get_report_or_404(pk)

    permission_check = _utils.check_admin_permission(request)
    if permission_check:
        return permission_check

    public.mark_report_as_read(report)
    messages.success(request, REPORT_MARKED_READ)
    return redirect(get_url_full(REPORT_LIST_NAME))


@login_required
def mark_as_unread(request, pk):
    """Vista para marcar un reporte como no leído."""
    report = _utils.get_report_or_404(pk)

    permission_check = _utils.check_admin_permission(request)
    if permission_check:
        return permission_check

    public.mark_report_as_unread(report)
    messages.success(request, REPORT_MARKED_UNREAD)
    return redirect(get_url_full(REPORT_LIST_NAME))
