from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Event
from .forms import EventForm
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q


def event_list(request):
    """Returns JSON list of events (including recurrences) within the given date range."""

    start_str = request.GET.get("start")  # eg: 2025-01-26T00:00:00
    end_str = request.GET.get("end")  # eg: 2025-03-02T00:00:00

    def parse_dt_or_now(dt_string, default):
        if not dt_string:
            return default
        return (datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S"))

    start_dt = parse_dt_or_now(start_str, (datetime.now()))
    end_dt = parse_dt_or_now(end_str, (
        datetime.now() + timedelta(days=30)))

    events_data = []

    # Get all events that fall within the date range
    events = Event.objects.all()

    for event in events:
        # Add the base event itself
        events_data.append({
            "id": event.id,
            "start": event.start_datetime.strftime('%Y-%m-%d %H:%M'),
            "end": event.end_datetime.strftime('%Y-%m-%d %H:%M') if event.end_datetime else event.start_datetime.strftime('%Y-%m-%d %H:%M'),
            "title": event.name,
        })

        # If the event is recurring, generate recurrences
        if event.recurrence:
            recurrences = event.recurrence.between(
                start_dt, end_dt, inc=False, dtstart=datetime(2010, 1, 1, 0, 0, 0),)

            for recurrence in recurrences:
                events_data.append({
                    "id": f'{event.id}{recurrence.isoformat()}',
                    "start": recurrence.strftime('%Y-%m-%d %H:%M'),
                    # Recurrence instances usually don't have an explicit end
                    "end": recurrence.strftime('%Y-%m-%d %H:%M'),
                    "title": event.name,
                })

    return JsonResponse(events_data, safe=False)


@csrf_exempt  # If using pure API, you may need CSRF exemption, but for forms it's not needed
def add_event(request):
    """Handles event creation via both JSON and form submission"""
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"message": "Event created successfully"}, status=201)
        else:
            return JsonResponse({"errors": form.errors}, status=400)
    else:
        form = EventForm()
    return render(request, "add_event.html", {"form": form})


def calendar(request):

    return render(request, 'calendar.html')
