import csv
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from TriNetra.database import initialize_database, insert_scan_results
from TriNetra.scanner import parse_port_range, resolve_target, scan_ports

from .forms import HistoryFilterForm, ScanForm
from .models import Scan
from .services import get_service_name

def scan_view(request):
    form = ScanForm(request.POST or None)
    is_async_request = (
        request.headers.get("x-requested-with") == "XMLHttpRequest"
        or "application/json" in request.headers.get("accept", "")
    )
    context = {
        "form": form,
        "results": [],
        "open_count": 0,
        "closed_count": 0,
        "saved_rows": 0,
        "resolved_ip": "",
        "target": "",
        "error": "",
    }

    db_path = str(Path(settings.DATABASES["default"]["NAME"]))
    initialize_database(db_path)

    if request.method == "POST" and form.is_valid():
        target = form.cleaned_data["target"].strip()
        ports_raw = form.cleaned_data["ports"].strip()
        timeout = form.cleaned_data["timeout"]

        try:
            ports = parse_port_range(ports_raw)
            if len(ports) > 4096:
                raise ValueError("Port list too large. Please scan 4096 ports or fewer per request.")

            resolved_ip = resolve_target(target)
            results = scan_ports(resolved_ip, ports, timeout)
            scan_timestamp = datetime.now(timezone.utc).isoformat()
            saved_rows = insert_scan_results(db_path, target, results, timestamp=scan_timestamp)
        except ValueError as error:
            context["error"] = str(error)
            if is_async_request:
                return JsonResponse({"ok": False, "error": context["error"]}, status=400)
            return render(request, "scanner/scan.html", context)
        except OSError as error:
            context["error"] = f"Network error: {error}"
            if is_async_request:
                return JsonResponse({"ok": False, "error": context["error"]}, status=400)
            return render(request, "scanner/scan.html", context)

        open_count = sum(1 for _, _, status in results if status == "OPEN")
        closed_count = len(results) - open_count
        request.session["latest_scan_target"] = target
        request.session["latest_scan_timestamp"] = scan_timestamp
        ui_results = [
            {
                "port": port,
                "status": status,
                "service": service or get_service_name(port),
                "timestamp": scan_timestamp,
            }
            for port, service, status in results
        ]

        context.update(
            {
                "results": ui_results,
                "open_count": open_count,
                "closed_count": closed_count,
                "saved_rows": saved_rows,
                "resolved_ip": resolved_ip,
                "target": target,
            }
        )

        if is_async_request:
            return JsonResponse(
                {
                    "ok": True,
                    "results": ui_results,
                    "open_count": open_count,
                    "closed_count": closed_count,
                    "saved_rows": saved_rows,
                    "resolved_ip": resolved_ip,
                    "target": target,
                }
            )

    elif request.method == "POST" and not form.is_valid() and is_async_request:
        first_error = "Invalid scan request. Please review your inputs."
        if form.errors:
            first_key = next(iter(form.errors))
            first_error = form.errors[first_key][0]
        return JsonResponse({"ok": False, "error": first_error}, status=400)

    return render(request, "scanner/scan.html", context)


def history_view(request):
    initialize_database(str(Path(settings.DATABASES["default"]["NAME"])))
    form = HistoryFilterForm(request.GET or None)
    scans = Scan.objects.all().only("target", "port", "status", "timestamp")

    if form.is_valid():
        target = (form.cleaned_data.get("target") or "").strip()
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if target:
            scans = scans.filter(target__icontains=target)
        if start_date:
            scans = scans.filter(timestamp__gte=start_date.isoformat())
        if end_date:
            end_exclusive = (end_date + timedelta(days=1)).isoformat()
            scans = scans.filter(timestamp__lt=end_exclusive)

    rows = scans[:500]
    history_rows = [
        {
            "id": item.id,
            "target": item.target,
            "port": item.port,
            "status": item.status,
            "timestamp": item.timestamp,
            "service": get_service_name(item.port),
        }
        for item in rows
    ]

    return render(
        request,
        "scanner/history.html",
        {
            "form": form,
            "scans": history_rows,
        },
    )


def _build_filtered_queryset(request):
    form = HistoryFilterForm(request.GET or None)
    scans = Scan.objects.all().only("target", "port", "status", "timestamp")

    if form.is_valid():
        target = (form.cleaned_data.get("target") or "").strip()
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")

        if target:
            scans = scans.filter(target__icontains=target)
        if start_date:
            scans = scans.filter(timestamp__gte=start_date.isoformat())
        if end_date:
            scans = scans.filter(timestamp__lt=(end_date + timedelta(days=1)).isoformat())

    return scans.order_by("-id")[:2000]


def export_scans_view(request):
    initialize_database(str(Path(settings.DATABASES["default"]["NAME"])))
    export_format = (request.GET.get("format") or "csv").lower()
    scope = (request.GET.get("scope") or "history").lower()

    if scope == "latest":
        latest_target = request.session.get("latest_scan_target")
        latest_timestamp = request.session.get("latest_scan_timestamp")
        queryset = Scan.objects.none()
        if latest_target and latest_timestamp:
            queryset = Scan.objects.filter(
                target=latest_target,
                timestamp=latest_timestamp,
            ).only("target", "port", "status", "timestamp")
    else:
        queryset = _build_filtered_queryset(request)

    rows = list(queryset)
    payload = [
        {
            "target": item.target,
            "port": item.port,
            "status": item.status,
            "service": get_service_name(item.port),
            "timestamp": item.timestamp,
        }
        for item in rows
    ]

    timestamp_label = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    if export_format == "json":
        response = HttpResponse(
            json.dumps(payload, indent=2),
            content_type="application/json",
        )
        response["Content-Disposition"] = f'attachment; filename="trinetra_export_{timestamp_label}.json"'
        return response

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="trinetra_export_{timestamp_label}.csv"'
    writer = csv.writer(response)
    writer.writerow(["target", "port", "status", "service", "timestamp"])
    for item in payload:
        writer.writerow([item["target"], item["port"], item["status"], item["service"], item["timestamp"]])

    return response


@require_POST
def delete_scan_view(request, scan_id: int):
    initialize_database(str(Path(settings.DATABASES["default"]["NAME"])))
    deleted_count, _ = Scan.objects.filter(id=scan_id).delete()

    if deleted_count == 0:
        return JsonResponse({"ok": False, "error": "Scan row not found."}, status=404)

    return JsonResponse({"ok": True, "deleted_id": scan_id})


@require_POST
def delete_all_scans_view(request):
    initialize_database(str(Path(settings.DATABASES["default"]["NAME"])))
    deleted_count, _ = Scan.objects.all().delete()
    return JsonResponse({"ok": True, "deleted_count": deleted_count})
