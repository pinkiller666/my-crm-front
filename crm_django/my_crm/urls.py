from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (event_list, add_event, calendar, home_page, mark_event_complete,
                    get_budget_info, progress_summary, artists, add_commission, commission_view,
                    progress_summary_full, EventViewSet, schedule_preview, get_users_with_schedule, TaskViewSet)

from django.views.i18n import JavaScriptCatalog

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'tasks', TaskViewSet)


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
    path('api/', include(router.urls)),
    path('api/schedule/preview/', schedule_preview, name='schedule-preview'),
    path("api/users-with-schedule/", get_users_with_schedule, name="users-with-schedule"),

]
