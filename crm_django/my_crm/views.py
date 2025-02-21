import plotly.offline as pyo
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
from .models import MoneyEvent, Account
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .weekdays import Weekday
from django.views import View
from .forms import MoneyEventForm
from django.contrib import messages
from django.urls import reverse
from .timeline_drawer import TimelineDrawer
from .money_event_handler import MoneyEventHandler, RepetitiveEventInstance
from django.db.models import Q

def parse_days_of_week(days_of_week_str):
    """
    Разбирает строку вида "понедельник, Wednesday, 5" в множество чисел {1, 3, 5},
    где 1 = Понедельник, 7 = Воскресенье.
    """
    if not days_of_week_str:
        return set()
    items = days_of_week_str.split(',')
    return {Weekday.get_day_number(item.strip()) for item in items if item.strip()}

def parse_specific_dates(dates_str):
    """ Разбирает строку вида "2025-01-15,2025-01-20" в список date-объектов."""
    if not dates_str:
        return []
    return [datetime.strptime(item.strip(), '%Y-%m-%d').date() for item in dates_str.split(',') if item.strip()]


def events_json(request):
    start_dt = datetime.fromisoformat(request.GET.get('start', datetime.now().isoformat()))
    end_dt = datetime.fromisoformat(request.GET.get('end', (datetime.now() + timedelta(days=30)).isoformat()))

    events = MoneyEvent.objects.filter(
        Q(single_event_date__date__gte=start_dt.date(), single_event_date__date__lte=end_dt.date()) |
        Q(start_repetition_date__gte=start_dt.date(), start_repetition_date__lte=end_dt.date()) |
        Q(end_repetition_date__gte=start_dt.date(), end_repetition_date__lte=end_dt.date())
    )



    # Convert queryset to JSON
    event_list = [
        {
            "id": event.id,
            "name": event.name,
            "start": event.single_event_date.isoformat() if event.single_event_date else None,
            "end": (
                    datetime.combine(event.single_event_date, event.doing_start_time) + timedelta(
                minutes=event.doing_duration_time)
            ).isoformat() if event.doing_start_time and event.doing_duration_time else event.single_event_date,
        }
        for event in events
    ]

    return JsonResponse(event_list, safe=False)


def timeline_view(request):
    """View, которое строит таймлайн из объекта MoneyEvent и рендерит шаблон."""

    events = MoneyEvent.objects.all()

    drawer = TimelineDrawer(events)
    fig = drawer.draw_timeline()
    plot_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)
    return render(request, 'timeline.html', {'plot_div': plot_div})

def create_money_event(request):
    if request.method == 'POST':
        print(request.POST)
        event_type = request.POST.get('eventType')  # single / repetitive / income

        # Общие поля
        name = request.POST.get('eventName')
        comment = request.POST.get('eventComment')
        tags_str = request.POST.get('tags', '')
        is_active = 'eventIsActive' in request.POST

        # Создаём MoneyEvent
        money_event = MoneyEvent()
        money_event.name = name
        money_event.comment = comment
        money_event.tags = tags_str
        money_event.event_is_active = is_active

        # Определяем, является ли событие повторяющимся
        money_event.is_repetitive = (event_type == 'repetitive')

        # Получаем время начала и продолжительность в зависимости от типа события
        doing_start_time = None
        doing_duration = None

        if event_type == 'single':
            doing_start_time = request.POST.get('singleStartTime')
            doing_duration = request.POST.get('singleDuration')
        elif event_type == 'repetitive':
            doing_start_time = request.POST.get('repetitiveStartTime')
            doing_duration = request.POST.get('repetitiveDuration')
        elif event_type == 'income':
            doing_start_time = request.POST.get('incomeStartTime')
            doing_duration = request.POST.get('incomeDuration')
        else:
            # Если тип вообще не распознан
            pass

        # Преобразуем в нужные типы (если пришли валидные значения)
        if doing_start_time:
            money_event.doing_start_time = datetime.strptime(doing_start_time, "%H:%M")
        if doing_duration:
            money_event.doing_duration_time = int(doing_duration)
        if doing_start_time and doing_duration:
            money_event.doing_end_time = money_event.doing_start_time + timedelta(minutes=money_event.doing_duration_time)

        # Обрабатываем логику по типу события
        if event_type == 'single':
            single_is_financial = 'singleIsFinancial' in request.POST
            account_id = request.POST.get("singleEventAccount")
            if single_is_financial:
                from decimal import Decimal
                raw_amount = request.POST.get('singleAmount', '0')
                amount = -abs(Decimal(raw_amount))  # Расход (отриц.)
            else:
                amount = None
            money_event.amount = amount
            money_event.single_event_date = request.POST.get('singleEventDate')

        elif event_type == 'repetitive':
            repetitive_is_financial = 'repetitiveIsFinancial' in request.POST
            account_id = request.POST.get("repetitiveEventAccount")
            if repetitive_is_financial:
                from decimal import Decimal
                raw_amount = request.POST.get('repetitiveAmount', '0')
                amount = -abs(Decimal(raw_amount))  # Расход (отриц.)
            else:
                amount = None
            money_event.amount = amount

            # Дополнительные поля для «повторяющихся» событий
            money_event.repetitive_type = request.POST.get('repetitiveTypeRadio')
            if money_event.repetitive_type == 'days_of_week':
                money_event.repetition_days_of_week = request.POST.get('days_of_week')
            elif money_event.repetitive_type == 'very_date':
                money_event.repetition_dates_of_month = request.POST.get('dates')
            elif money_event.repetitive_type == 'n_days':
                money_event.repetition_interval_days = request.POST.get('n_days')
            money_event.start_date = request.POST.get('repetitiveStartDate')
            money_event.end_date = request.POST.get('repetitiveEndDate')

        else:  # income
            # Здесь всегда финансовое, всегда положительное
            if event_type == 'income':
                account_id = request.POST.get("incomeEventAccount")
                from decimal import Decimal
                raw_amount = request.POST.get('incomeAmount', '0')
                amount = abs(Decimal(raw_amount))
                money_event.amount = amount
            else:
                # Если вдруг не single, не repetitive, не income — account_id не определён
                account_id = None

        # Связываем с аккаунтом, если указан
        if account_id:
            money_event.account = Account.objects.get(id=account_id)

        money_event.save()

        if money_event.is_repetitive:
            MEH = MoneyEventHandler(money_event.start_repetition_date, money_event.end_repetition_date)
            filtered_and_generated_events = MEH._generate_repetitive_event_instances(money_event)

            # Prepare common event data
            event_data = {
                "parent": money_event,
                "name": money_event.name,
                "amount": money_event.amount,
                "comment": money_event.comment,
                "tags": money_event.tags,
                "event_is_active": money_event.event_is_active,
                "event_status": money_event.event_status,
                "account": money_event.account,
                "doing_start_time": money_event.doing_start_time,
                "doing_duration_time": money_event.doing_duration_time,
                "doing_end_time": money_event.doing_end_time,
            }

            # Generate child events
            child_events = [
                MoneyEvent(**event_data, single_event_date=rep_event.single_event_date)
                for rep_event in filtered_and_generated_events
            ]

            MoneyEvent.objects.bulk_create(child_events)  # Efficient bulk insertion

            messages.success(request, "Новое событие создано УСПЕШНО")


        # После сохранения — редирект в админку
        return redirect('/')

    else:
        # Если GET — просто рендерим форму
        accounts = Account.objects.all()
        return render(request, 'create_event.html', {'accounts': accounts})

def timeline_new_view(request):
    today = datetime.today().date()
    start_of_month = today.replace(day=1)

    days = []
    current_date = start_of_month
    days_in_month = 0

    while current_date.month == start_of_month.month:
        days_in_month += 1
        current_date += timedelta(days=1)

    weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    day_list = []

    for i in range(1, days_in_month + 1):
        date_obj = start_of_month.replace(day=i)
        position_percent = round((i - 1) / (days_in_month - 1) * 100, 2)

        weekday_index = date_obj.weekday()
        weekday_label = weekdays[weekday_index]

        day_list.append({
            'day_number': i,
            'weekday_short': weekday_label,
            'position': position_percent,
            'is_today': date_obj == today
        })

    return render(request, 'timeline_new.html', {'days': day_list})
