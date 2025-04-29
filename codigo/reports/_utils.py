"""
Funciones de utilidad internas para la aplicación de reportes.
"""

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone

from .constants import (CREATE_REPORT_NAME, DELETE_REPORT_NAME,
                        IMPORTANT_IMPORTANCE, MARK_READ_NAME, MARK_UNREAD_NAME,
                        NO_MARK_PERMISSION_ERROR, NO_PERMISSION_ERROR,
                        NO_VIEW_PERMISSION_ERROR, NORMAL_IMPORTANCE,
                        PAYMENT_ID_PARAM, PAYMENT_TYPE,
                        REPORT_ALREADY_RESPONDED_ERROR, REPORT_CREATED_SUCCESS,
                        REPORT_DELETED_SUCCESS, REPORT_DETAIL_NAME,
                        REPORT_LIST_NAME, REPORT_MARKED_READ,
                        REPORT_MARKED_UNREAD, REPORTS_PER_PAGE,
                        RESPONSE_SENT_SUCCESS, RIDE_ID_PARAM, RIDE_TYPE,
                        SYSTEM_TYPE, UPDATE_REPORT_NAME, URGENT_IMPORTANCE,
                        USER_ID_PARAM, USER_TYPE, get_url_full)
from .forms import ReportFilterForm, ReportForm, ReportResponseForm
from .models import Report


def get_report_or_404(pk):
    """
    Obtiene un reporte o devuelve un 404.
    """
    return get_object_or_404(Report, pk=pk)


def check_report_view_permission(request, report):
    """
    Verifica que el usuario tenga permiso para ver el reporte.
    """
    if not (request.user.is_staff or request.user == report.user):
        return HttpResponseForbidden(NO_VIEW_PERMISSION_ERROR)
    return None


def check_report_edit_permission(request, report):
    """
    Verifica que el usuario tenga permiso para editar el reporte.
    """
    # Solo el creador o un admin pueden editar
    if not (request.user.is_staff or request.user == report.user):
        return HttpResponseForbidden(NO_PERMISSION_ERROR)

    # No se puede editar si ya tiene respuesta
    if report.response and not request.user.is_staff:
        messages.warning(request, REPORT_ALREADY_RESPONDED_ERROR)
        return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)

    return None


def check_admin_permission(request):
    """
    Verifica que el usuario sea un administrador.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden(NO_MARK_PERMISSION_ERROR)
    return None


def filter_reports(request, reports):
    """
    Aplica filtros a los reportes según los parámetros GET.
    """
    filter_form = ReportFilterForm(request.GET)

    # Guardar copia del queryset original para comparación
    original_count = reports.count()

    if filter_form.is_valid():
        # Filtrar por tipo
        if report_type := request.GET.get("report_type"):
            reports = reports.filter(report_type=report_type)

        # SOLUCIÓN DEFINITIVA para el filtro de importancia
        # Usar valores directos en la consulta SQL con valores 1, 2, 3
        if importance := request.GET.get("importance"):
            if importance == "1":
                # Mostrar todos los reportes con importancia "normal"
                # Usar consulta directa para evitar problemas de mapeo
                from django.db.models import Q

                reports = reports.filter(
                    Q(importance="normal") | Q(importance=Report.NORMAL)
                )
            elif importance == "2":
                # Mostrar todos los reportes con importancia "important"
                from django.db.models import Q

                reports = reports.filter(
                    Q(importance="important") | Q(importance=Report.IMPORTANT)
                )
            elif importance == "3":
                # Mostrar todos los reportes con importancia "urgent"
                from django.db.models import Q

                reports = reports.filter(
                    Q(importance="urgent") | Q(importance=Report.URGENT)
                )

        # Filtrar por estado (leído/no leído/respondido)
        if status := request.GET.get("status"):
            if status == "unread":
                reports = reports.filter(read=False)
            elif status == "read":
                reports = reports.filter(read=True)
            elif status == "responded":
                reports = reports.filter(response__isnull=False).exclude(response="")

        # Búsqueda de texto
        if search := request.GET.get("search"):
            reports = reports.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )

    # Registrar información sobre el filtrado para diagnóstico
    filtered_count = reports.count()
    if request.GET.get("importance"):
        importance_value = request.GET.get("importance")
        print(f"\n--- FILTRO DE IMPORTANCIA APLICADO ---")
        print(f"Valor del filtro: '{importance_value}'")
        print(f"Reportes antes: {original_count}, después: {filtered_count}")

        # Mostrar las IMPORTANCE_CHOICES definidas en el modelo Report
        print(
            f"Valores de importancia definidos en el modelo: {Report.IMPORTANCE_CHOICES}"
        )

        # Imprimir valores de importancia de algunos reportes para diagnóstico
        for report in Report.objects.all()[:3]:
            print(f"Reporte ID {report.id}: importance='{report.importance}'")

    return reports, filter_form


def paginate_reports(request, reports):
    """
    Pagina los reportes.
    """
    paginator = Paginator(reports, REPORTS_PER_PAGE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def prepare_report_context(report, user):
    """
    Prepara el contexto para la vista de detalle de un reporte.
    """
    context = {
        "report": report,
        "is_admin": user.is_staff,
    }

    if user.is_staff:
        context["response_form"] = ReportResponseForm(instance=report)

    return context


def prepare_report_list_context(page_obj, filter_form, user):
    """
    Prepara el contexto para la vista de lista de reportes.
    """
    return {
        "reports": page_obj,
        "filter_form": filter_form,
        "page_obj": page_obj,
        "is_paginated": page_obj.paginator.num_pages > 1,
        "paginator": page_obj.paginator,
        "is_admin": user.is_staff,
    }


def handle_report_response(request, report):
    """
    Maneja la respuesta a un reporte.
    """
    if not request.user.is_staff:
        return HttpResponseForbidden(NO_PERMISSION_ERROR)

    response_form = ReportResponseForm(request.POST, instance=report)
    if response_form.is_valid():
        report_response = response_form.save(commit=False)
        report_response.response_by = request.user
        report_response.response_at = timezone.now()
        report_response.save()
        messages.success(request, RESPONSE_SENT_SUCCESS)
        return redirect(get_url_full(REPORT_DETAIL_NAME), pk=report.pk)

    return None


def get_related_objects(request):
    """
    Obtiene objetos relacionados para un reporte (usuario, viaje, pago).
    """
    from django.contrib.auth.models import User
    from payments.models import Payment
    from rides.models import Ride

    reported_user = None
    ride = None
    payment = None
    initial_data = {}

    user_id = request.GET.get(USER_ID_PARAM)
    ride_id = request.GET.get(RIDE_ID_PARAM)
    payment_id = request.GET.get(PAYMENT_ID_PARAM)

    if user_id:
        reported_user = get_object_or_404(User, pk=user_id)
        initial_data["report_type"] = Report.USER
        initial_data["title"] = f"Reporte sobre usuario: {reported_user.username}"
    elif ride_id:
        ride = get_object_or_404(Ride, pk=ride_id)
        initial_data["report_type"] = Report.RIDE
        initial_data["title"] = (
            f"Reporte sobre viaje: {ride.origin} a {ride.destination}"
        )
    elif payment_id:
        payment = get_object_or_404(Payment, pk=payment_id)
        initial_data["report_type"] = Report.PAYMENT
        initial_data["title"] = (
            f"Reporte sobre pago de {payment.amount}€ a {payment.recipient.username}"
        )

    return reported_user, ride, payment, initial_data


def prepare_create_report_context(form, reported_user, ride, payment):
    """
    Prepara el contexto para la vista de creación de un reporte.
    """
    return {
        "form": form,
        "reported_user": reported_user,
        "ride": ride,
        "payment": payment,
    }
