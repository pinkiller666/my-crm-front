from django.urls import path
from .views import (event_list, add_event, calendar, home_page, mark_event_complete,
                    get_budget_info, progress_summary, artists, add_commission, commission_view,
                    progress_summary_full)

from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("calendar/", calendar, name="calendar"),
    path("events/", event_list, name="events_json"),
    path("events/add/", add_event, name="add-event"),
    path('jsi18n.js', JavaScriptCatalog.as_view(
        packages=['recurrence']), name='jsi18n'),
    path("", home_page, name="Home page"),
    # использовать надо url_for в шаблонах,
    path('mark_event_complete/<int:event_id>/', mark_event_complete, name='mark_event_complete'),
    path('get_budget', get_budget_info, name='обновить_инфу_бюджета'),
    path('api/artists/', artists, name='artist'),
    path('api/progress/', commission_view, name='progress'),
    path('api/progress-full/', progress_summary_full, name='progress-full'),
]
