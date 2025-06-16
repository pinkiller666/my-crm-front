from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework import status

from .models import Event, CompletionStatus, EventInstance
from .forms import EventForm
from datetime import datetime, timedelta
from django.utils.timezone import make_aware
from django.db.models import Q
from .one_month_check import get_main_month
from .api.progress_api import get_month_progress, get_artist_for_progres, get_month_progress_full
from .weekdays import Weekday


from django.utils.timezone import make_aware, is_naive
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.utils import timezone
from .models import Artist, AcceptedCommission
from rest_framework import viewsets
from .serializers import EventSerializer

from .utils.schedule_helper import generate_day_types, return_pattern, return_groups_by_pattern
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import MonthSchedule

from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

User = get_user_model()


def event_list(request):
    """Возвращает JSON-список событий, учитывая экземпляры выполненных событий."""

    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    def parse_dt_or_now(dt_string, default):
        if not dt_string:
            return default
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=None)  # Делаем naive

    start_dt = parse_dt_or_now(start_str, timezone.now().replace(tzinfo=None))
    end_dt = parse_dt_or_now(end_str, (timezone.now() + timedelta(days=30)).replace(tzinfo=None))

    events_data = []
    events = Event.objects.all()
    instances = EventInstance.objects.all()

    for event in events:
        base_event = {
            "id": event.id,
            "start": event.start_datetime.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M'),
            "end": event.end_datetime.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M') if event.end_datetime else event.start_datetime.replace(tzinfo=None).strftime('%Y-%m-%d %H:%M'),
            "title": event.name,
            "status": event.status
        }
        if not event.recurrence:
            events_data.append(base_event)

        if event.recurrence:
            recurrences = event.recurrence.between(start_dt, end_dt, inc=True, dtstart=datetime(2010, 1, 1, 0, 0, 0))

            for recurrence in recurrences:
                recurrence = recurrence.replace(tzinfo=None)  # Делаем naive

                instance = instances.filter(parent_event=event, instance_datetime=recurrence).first()

                events_data.append({
                    "id": event.id,
                    "start": recurrence.strftime('%Y-%m-%d %H:%M'),
                    "end": recurrence.strftime('%Y-%m-%d %H:%M'),
                    "title": event.name,
                    "status": instance.status if instance else event.status
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


def home_page(request):

    return render(request, 'timeline.html')


@csrf_exempt
def mark_event_complete(request, event_id):
    if request.method == "POST":
        try:
            event = get_object_or_404(Event, pk=event_id)
            instance_datetime = request.POST.get("instance_datetime")  # Получаем дату фейкового события

            if not instance_datetime:
                return JsonResponse({"success": False, "error": "Не указана дата события"}, status=400)

            try:
                instance_datetime = datetime.strptime(instance_datetime, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return JsonResponse({"success": False, "error": "Некорректный формат даты"}, status=400)

            # Проверяем, есть ли уже измененный экземпляр
            instance, created = EventInstance.objects.get_or_create(
                parent_event=event,
                instance_datetime=instance_datetime,
                defaults={"status": CompletionStatus.COMPLETE}
            )

            if not created:  # Если экземпляр уже был, просто обновляем статус
                instance.status = CompletionStatus.COMPLETE
                instance.save()

            return JsonResponse({"success": True})
        except Event.DoesNotExist:
            return JsonResponse({"success": False, "error": "Событие не найдено"}, status=404)

    return JsonResponse({"success": False, "error": "Неверный метод запроса"}, status=400)


def get_budget_info(request):
    """Возвращает JSON-список событий, учитывая экземпляры выполненных событий."""

    start_str = request.GET.get("start")
    end_str = request.GET.get("end")

    def parse_dt_or_now(dt_string, default):
        if not dt_string:
            return default
        dt = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S")
        return dt.replace(tzinfo=None)  # Делаем naive

    start_dt = parse_dt_or_now(start_str, timezone.now().replace(tzinfo=None))
    end_dt = parse_dt_or_now(end_str, (timezone.now() + timedelta(days=30)).replace(tzinfo=None))
    print(start_dt, end_dt)
    year_and_month = get_main_month(start_dt, end_dt)
    current_events = get_events_in_range(year_and_month["year"], year_and_month["month"])
    print(current_events)
    income = 0
    expense = 0
    for event in current_events:
        if event['event'].amount > 0.0:
            print('INCOME!!!', event['event'].amount)
            income += event['event'].amount
        else:
            expense += (-1)*(event['event'].amount)
    print("income: ", income)
    print("expense: ", expense)
    return JsonResponse({"income": income, "expense": expense}, status=200)


def get_events_in_range(year: int, month: int):
    """
    Получает все события и их повторения, которые попадают в указанный месяц.
    """

    # Определяем границы месяца (начало и конец) и делаем их naive
    start_dt = datetime(year, month, 1)
    next_month = (start_dt + timedelta(days=32)).replace(day=1)
    end_dt = next_month - timedelta(seconds=1)

    # Приводим все event.start_datetime к naive (убираем таймзону)
    def make_naive(dt):
        return dt.replace(tzinfo=None) if dt.tzinfo else dt

    # Получаем все события, которые:
    # 1. Начинаются в заданном диапазоне
    # 2. Имеют рецуррентные повторения, попадающие в диапазон
    events_data = []

    events = Event.objects.filter(
        Q(start_datetime__lte=end_dt) &
        (Q(end_datetime__gte=start_dt) | Q(end_datetime__isnull=True))
    )

    for event in events:
        event_start_naive = make_naive(event.start_datetime)

        # Базовое событие, если оно само попадает в диапазон
        if start_dt <= event_start_naive <= end_dt:
            if not event.recurrence:
                events_data.append({
                "id": event.id,
                "event": event
            })

        # Обрабатываем рецуррентные повторения (если есть `recurrence`)
        if event.recurrence:
            recurrences = event.recurrence.between(start_dt, end_dt, inc=True, dtstart=datetime(2010, 1, 1, 0, 0, 0))
            for recurrence in recurrences:
                recurrence_naive = make_naive(recurrence)

                events_data.append({
                    "id": event.id,
                    "date": recurrence_naive.strftime('%Y-%m-%d %H:%M'),
                "event": event
                })

    return events_data


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def progress_summary(request):
    data = get_month_progress()
    return Response(data)


@api_view(['GET', 'POST'])
@renderer_classes([JSONRenderer])
def commission_view(request):
    if request.method == 'GET':
        return Response(get_month_progress())

    elif request.method == 'POST':
        data = request.data
        print('[DEBUG] Получены данные:', request.data)

        artist = data.get('artist')
        amount = data.get('amount')
        comment = data.get('comment', '')

        try:
            artist = int(artist)
            amount = int(amount)
        except (ValueError, TypeError):
            return Response({'error': 'Неверный формат данных'}, status=400)

        if not artist or not isinstance(artist, int):
            return Response({'error': 'Некорректный художник (id)'}, status=status.HTTP_400_BAD_REQUEST)

        if not Artist.objects.filter(id=artist).exists():
            return Response({'error': 'Художник не найден'}, status=404)

        if not isinstance(amount, int) or amount < 1 or amount > 99999:
            return Response({'error': 'Сумма должна быть целым числом от 1 до 99999'}, status=status.HTTP_400_BAD_REQUEST)

        if comment and len(comment) > 500:
            return Response({'error': 'Комментарий слишком длинный (макс. 500 символов)'}, status=status.HTTP_400_BAD_REQUEST)

        commission = AcceptedCommission.objects.create(
            artist_id=artist,
            amount=amount,
            comment=comment
        )

        return Response({'status': 'ok', 'id': commission.id}, status=status.HTTP_201_CREATED)




@api_view(['GET'])
@renderer_classes([JSONRenderer])
def artists(request):
    artist_list = get_artist_for_progres()
    return Response(artist_list)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def add_commission(request):
    data = request.data
    print('[DEBUG] Получены данные:', request.data)

    artist = data.get('artist')
    amount = data.get('amount')
    comment = data.get('comment', '')

    try:
        artist = int(artist)
        amount = int(amount)
    except (ValueError, TypeError):
        return Response({'error': 'Неверный формат данных'}, status=400)

    # 🔎 Проверка: artist должен быть int
    if not artist or not isinstance(artist, int):
        return Response({'error': 'Некорректный художник (id)'}, status=status.HTTP_400_BAD_REQUEST)

    # 🔍 Существует ли художник?
    if not Artist.objects.filter(id=artist).exists():
        return Response({'error': 'Художник не найден'}, status=404)

    # 💵 Валидация суммы
    if not isinstance(amount, int) or amount < 1 or amount > 99999:
        return Response({'error': 'Сумма должна быть целым числом от 1 до 99999'}, status=status.HTTP_400_BAD_REQUEST)

    # 🗨 Проверка длины комментария (если есть)
    if comment and len(comment) > 500:
        return Response({'error': 'Комментарий слишком длинный (макс. 500 символов)'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Создание комиссии
    commission = AcceptedCommission.objects.create(
        artist_id=artist,
        amount=amount,
        comment=comment
    )

    return Response({
        'status': 'ok',
        'id': commission.id
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@renderer_classes([JSONRenderer])
def progress_summary_full(request):
    return Response(get_month_progress_full())


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-start_datetime')
    serializer_class = EventSerializer


@api_view(['GET'])
def schedule_preview(request):
    """
    Возвращает предварительный просмотр расписания за указанный год и месяц.
    В ответе:
    - список дней с типами (work/off),
    - pattern для фронта,
    - группы (размеры логических блоков).
    """
    user_id = request.query_params.get('user')

    try:
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))
        user_id = int(user_id) if user_id is not None else None
    except (ValueError, TypeError):
        return Response({'error': 'Неверные параметры year/month/user'}, status=400)

    if user_id is None:
        return Response({'error': 'Параметр user обязателен'}, status=400)

    schedule = MonthSchedule.objects.filter(user=user_id, year=year, month=month).first()

    if not schedule:
        return Response({'error': 'Расписание не найдено'}, status=404)

    result = generate_day_types(schedule)

    days = [
        {
            'date': d.isoformat(),
            'day': d.day,
            'type': t,
            'weekday': Weekday.get_day_by_number(d.isoweekday(), format_type='short_RU')
        }
        for d, t in result
    ]

    pattern = return_pattern(schedule)
    groups = return_groups_by_pattern(schedule)

    return Response({
        'days': days,
        'pattern': pattern,
        'groups': groups
    }, status=200)


def get_users_with_schedule(request):
    users = User.objects.filter(
        Q(as_artist__isnull=False) | Q(as_manager__isnull=False)
    ).distinct()

    data = [
        {
            "id": user.id,
            "name": user.username,
            "roles": [
                role for role, exists in [
                    ("artist", hasattr(user, "as_artist")),
                    ("manager", hasattr(user, "as_manager")),
                    ("middleman", hasattr(user, "as_middleman")),
                ] if exists
            ]
        }
        for user in users
    ]

    return JsonResponse(data, safe=False)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('date_day', 'start_datetime')
    serializer_class = TaskSerializer
