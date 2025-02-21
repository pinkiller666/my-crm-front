from django.urls import path
from .views import timeline_view, create_money_event, events_json, timeline_new_view


urlpatterns = [
    path('', timeline_view, name='timeline'),
    path('create-event/', create_money_event, name='moneyevent_create'),
    path('calendar/events/', events_json, name='events_json'),
    path('timeline_new/', timeline_new_view, name='timeline_new')
    # использовать надо url_for в шаблонах,
]