from django.urls import path
from .views import event_list, add_event, calendar
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("calendar/", calendar, name="calendar"),
    path("events/", event_list, name="events_json"),
    path("events/add/", add_event, name="add-event"),
    path('jsi18n.js', JavaScriptCatalog.as_view(
        packages=['recurrence']), name='jsi18n'),
]
