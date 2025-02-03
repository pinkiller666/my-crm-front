import plotly.offline as pyo
import plotly.graph_objects as go
from datetime import datetime, timedelta, time
from .models import MoneyEvent
from .models import Account
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from .forms import MoneyEventForm
from django.contrib import messages
from django.urls import reverse


def get_money_events():
    events = MoneyEvent.objects.all().order_by('event_date')
    return [{'date': event.event_date.isoformat(), 'name': str(event)} for event in events]


class TimelineDrawer:
    def __init__(self, events):
        """
        events — список словарей вида:
        [
            {"date": "2023-12-01", "name": "Мероприятие X"},
            {"date": "2023-12-05", "name": "Мероприятие Y"},
            ...
        ]
        """
        self.events = events
        self.dates = [datetime.strptime(event["date"], "%Y-%m-%d") for event in self.events]
        self.names = [event["name"] for event in self.events]

        # Точка "сегодня" (без часов/минут)
        self.today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        # Примерная логика для start_date и end_date:
        # - берём "сегодня" и смещаемся назад на ~7 дней и вперёд на ~40.
        # - плюс в примере вы делали replace(day=1) и т.п. — оставим это как есть:
        self.start_date = (self.today.replace(day=1) - timedelta(days=7)).replace(day=25)
        self.end_date = (self.today.replace(day=1) + timedelta(days=40)).replace(day=15)

        # Генерируем «линейку» дат с шагом в 1 день
        self.tick_dates = [
            self.start_date + timedelta(days=i)
            for i in range((self.end_date - self.start_date).days + 1)
        ]

        # Сгруппируем события по датам
        self.events_by_date = self.group_events_by_date()

    def group_events_by_date(self):
        grouped = {}
        for event, date in zip(self.names, self.dates):
            if date in grouped:
                grouped[date].append(event)
            else:
                grouped[date] = [event]
        return grouped

    def draw_timeline(self):
        fig = go.Figure()

        # Фоновые «подсветки» месяцев
        self.add_month_backgrounds(fig)

        # Линия времени (розовая горизонтальная)
        fig.add_trace(go.Scatter(
            x=[self.tick_dates[0], self.tick_dates[-1]],
            y=[0, 0],
            mode="lines",
            line=dict(color="pink", width=2),
            name="Линия времени"
        ))

        # Вертикальные деления для каждого дня (с надписью дня месяца)
        self.add_day_ticks(fig)

        # Сами события (красные точки + подписи)
        self.add_events(fig)

        # «Сейчас» — вертикальная линия (с надписью «Сегодняшний день»)
        self.add_today_marker(fig)

        # Настройки оформления осей и высоты
        fig.update_layout(
            title="Временная линия",
            xaxis_title="",
            yaxis=dict(visible=False),
            xaxis=dict(
                showgrid=True,
                zeroline=False,
                showline=True,
                showticklabels=False,
                range=[self.start_date, self.end_date],
            ),
            plot_bgcolor="white",
            height=400
        )

        return fig

    def add_month_backgrounds(self, fig):
        # Заливка под каждый день, в примере логика: текущий месяц (розоватый),
        # прошлый и следующий — зеленоватые
        for date in self.tick_dates:
            if date.month == self.today.month:
                color = "rgba(255, 192, 203, 0.2)"  # Розовый для текущего месяца
            elif date < self.today.replace(day=1):
                color = "rgba(144, 238, 144, 0.2)"  # Зелёный для предыдущего месяца
            else:
                color = "rgba(144, 238, 144, 0.2)"  # Зелёный для следующего месяца

            fig.add_shape(
                type="rect",
                x0=date,
                x1=date + timedelta(days=1),
                y0=-1,
                y1=1,
                fillcolor=color,
                line=dict(width=0),
                layer="below"
            )

    def add_day_ticks(self, fig):
        for date in self.tick_dates:
            line_length = 0.2
            color = "gray"
            text_size = 12

            # Скажем, если это 1-е число месяца — шрифт побольше:
            if date.day == 1:
                text_size = 32

            fig.add_trace(go.Scatter(
                x=[date, date],
                y=[-line_length, line_length],
                mode="lines+text",
                line=dict(color=color, width=1),
                text=[str(date.day)],
                textposition="bottom center",
                textfont=dict(family="Comfortaa", size=text_size, color="gray", weight="bold"),
                showlegend=False
            ))

    def add_events(self, fig):
        # Раскладываем события в пределах одного дня «по Y», чтобы не наслаивались
        for date, events in self.events_by_date.items():
            num_events = len(events)
            if num_events > 1:
                offsets = [i * 0.3 / (num_events - 1) - 0.15 for i in range(num_events)]
            else:
                offsets = [0]

            for event, offset in zip(events, offsets):
                fig.add_trace(go.Scatter(
                    x=[date + timedelta(hours=12)],  # Сдвиг в полдень
                    y=[offset],
                    mode="markers+text",
                    marker=dict(size=10, color="red"),
                    text=[event],
                    textposition="top center",
                    textfont=dict(family="Comfortaa", size=12, color="black"),
                    showlegend=False
                ))

    def add_today_marker(self, fig):
        fig.add_shape(
            type="line",
            x0=self.today,
            x1=self.today,
            y0=-0.5,
            y1=1,
            line=dict(color="#FF69B4", width=4, dash="solid"),
            layer="above"
        )
        fig.add_trace(go.Scatter(
            x=[self.today],
            y=[-0.7],
            mode="text",
            text=["Сегодняшний день"],
            textfont=dict(family="Comfortaa", size=20, color="pink"),
            showlegend=False
        ))


def timeline_view(request):
    """View, которое строит таймлайн из объекта MoneyEvent и рендерит шаблон."""

    # Забираем все события. Можно фильтровать, сортировать и т.п.
    # Предположим, что model MoneyEvent имеет поля: name, event_date, ...
    qs = MoneyEvent.objects.all().order_by('event_date')

    # Преобразуем queryset в нужный формат, чтоб совпадал с тем, что ожидает TimelineDrawer
    # Обратите внимание, что TimelineDrawer ждёт строку вида "YYYY-MM-DD"
    events_list = [
        {"date": e.event_date.strftime("%Y-%m-%d"), "name": e.name}
        for e in qs
    ]

    # Создаём инстанс класса для рисования
    drawer = TimelineDrawer(events_list)

    # Генерируем сам график
    fig = drawer.draw_timeline()

    # Превращаем его в HTML-код (div), чтобы вставить в шаблон
    plot_div = pyo.plot(fig, output_type='div', include_plotlyjs=False)

    # Рендерим шаблон и передаём туда plot_div
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
        money_event.is_active = is_active

        # Определяем, является ли событие повторяющимся
        money_event.is_repetitive = (event_type == 'repetitive')

        # Получаем время начала и продолжительность в зависимости от типа события
        start_time = None
        duration = None

        if event_type == 'single':
            start_time = request.POST.get('singleStartTime')
            duration = request.POST.get('singleDuration')
        elif event_type == 'repetitive':
            start_time = request.POST.get('repetitiveStartTime')
            duration = request.POST.get('repetitiveDuration')
        elif event_type == 'income':
            start_time = request.POST.get('incomeStartTime')
            duration = request.POST.get('incomeDuration')
        else:
            # Если тип вообще не распознан
            pass

        # Преобразуем в нужные типы (если пришли валидные значения)
        if start_time:
            money_event.start_time = datetime.strptime(start_time, "%H:%M")
        if duration:
            money_event.duration = int(duration)

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
            money_event.event_date = request.POST.get('singleEventDate')

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
                money_event.days_of_week = request.POST.get('days_of_week')
            elif money_event.repetitive_type == 'very_date':
                money_event.dates = request.POST.get('dates')
            elif money_event.repetitive_type == 'n_days':
                money_event.n_days = request.POST.get('n_days')
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

        # После сохранения — редирект в админку
        # return redirect('admin:index')
        return render(request,'timeline.html')

    else:
        # Если GET — просто рендерим форму
        accounts = Account.objects.all()
        return render(request, 'create_event.html', {'accounts': accounts})


def events_json(request):
    """
    Представление для отдачи событий с учётом разных типов повторения:
    - одиночные события (is_repetitive=False)
    - повтор по дням недели (repetitive_type='po_dnyam_nedeli')
    - повтор по конкретным датам (repetitive_type='po_konkret_dnyam')
    - повтор каждые n дней (repetitive_type='po_kazhdy_n_dney')
    и т.п.

    Параметры start, end (например: 2025-01-26T00:00:00, 2025-03-02T00:00:00).
    """

    start_str = request.GET.get('start')  # например: 2025-01-26T00:00:00
    end_str = request.GET.get('end')  # например: 2025-03-02T00:00:00

    # Разберём дату через fromisoformat (Python 3.7+) или strptime
    # Здесь предполагается что приходит формат 2025-01-26T00:00:00 (без TZ)
    def parse_dt_or_now(dt_string, default):
        if not dt_string:
            return default
        # Если Python 3.7+ — можно так:
        #    return datetime.fromisoformat(dt_string)
        # Или через strptime, если T в формáte:
        return datetime.strptime(dt_string, '%Y-%m-%dT%H:%M:%S')

    start_dt = parse_dt_or_now(start_str, datetime.now())
    end_dt = parse_dt_or_now(end_str, datetime.now() + timedelta(days=30))

    all_events = MoneyEvent.objects.filter(is_active=True)
    event_list = []

    for event in all_events:
        # ----- 1. ОДИНОЧНОЕ СОБЫТИЕ -----
        if not event.is_repetitive:
            _add_single_event_if_in_range(event, start_dt, end_dt, event_list)
            continue

        # ----- 2. ПОВТОРЯЮЩИЕСЯ СОБЫТИЯ -----
        repetitive_type = event.repetitive_type

        # Для удобства получаем "базовый" диапазон повторений
        # (start_date, end_date) + (start_time, end_time)
        # Если у события они не заданы, fallback на start_dt / end_dt
        from_date = event.start_date if event.start_date else start_dt.date()
        to_date = event.end_date if event.end_date else end_dt.date()

        if event.start_time:
            series_current_dt = datetime.combine(from_date, event.start_time)
        else:
            series_current_dt = datetime.combine(from_date, time.min)

        if event.end_time and event.end_date:
            series_final_dt = datetime.combine(event.end_date, event.end_time)
        else:
            series_final_dt = datetime.combine(to_date, time.max)

        # Логика повторения зависит от repetitive_type
        # ---
        if repetitive_type == 'po_dnyam_nedeli':
            # Предположим, event.days_of_week = "0,2" означает понедельник (0) и среду (2)
            # (учитывая Python datetime.weekday(): Пн=0, Вт=1, Ср=2, Чт=3, Пт=4, Сб=5, Вс=6)
            day_of_week_nums = parse_days_of_week(event.days_of_week)  # см. функцию ниже

            # Шагаем по дням от series_current_dt до series_final_dt
            current_dt = series_current_dt
            while current_dt <= series_final_dt:
                # Если день недели current_dt в нашем списке (set), значит добавляем событие
                if current_dt.weekday() in day_of_week_nums:
                    _add_repetitive_occurrence_if_in_range(
                        event, current_dt, start_dt, end_dt, event_list
                    )
                current_dt += timedelta(days=1)

        elif repetitive_type == 'po_konkret_dnyam':
            # Допустим, event.dates = "2025-01-15,2025-01-20"
            # Парсим и для каждой даты (date) формируем datetime + start_time
            date_list = parse_specific_dates(event.dates)  # см. функцию ниже

            for d in date_list:
                # Проверяем, что дата в пределах [from_date, to_date]
                if from_date <= d <= to_date:
                    # Формируем datetime, учитывая start_time
                    if event.start_time:
                        occ_dt = datetime.combine(d, event.start_time)
                    else:
                        occ_dt = datetime.combine(d, time.min)

                    _add_repetitive_occurrence_if_in_range(
                        event, occ_dt, start_dt, end_dt, event_list
                    )

        elif repetitive_type == 'po_kazhdy_n_dney':
            # Допустим, n_days = 2 => повтор каждые 2 дня, пока не дойдём до end_date
            step_days = event.n_days if (event.n_days and event.n_days > 0) else 1
            current_dt = series_current_dt
            while current_dt <= series_final_dt:
                _add_repetitive_occurrence_if_in_range(
                    event, current_dt, start_dt, end_dt, event_list
                )
                current_dt += timedelta(days=step_days)

        else:
            # Если никакой из описанных типов не подошёл,
            # можно либо пропустить, либо сделать «повтор каждый день» по умолчанию, и т.п.
            pass

    return JsonResponse(event_list, safe=False)


# ----------------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ----------------------------------------------------------------

def _add_single_event_if_in_range(event, start_dt, end_dt, event_list):
    """
    Добавляет одиночное (неповторяющееся) событие, если оно пересекается
    с диапазоном [start_dt, end_dt].
    """
    start_event = event.event_date
    if event.duration and event.duration > 0:
        end_event = start_event + timedelta(minutes=event.duration)
    else:
        end_event = start_event

    # Проверка на пересечение интервалов:
    if end_event >= start_dt and start_event <= end_dt:
        event_list.append({
            'id': event.id,
            'title': event.name,
            'url': f"/money_event/{event.id}/",
            'class': 'income' if (event.amount and event.amount >= 0) else 'expense',
            'start': start_event.isoformat(),
            'end': end_event.isoformat(),
            'extendedProps': {
                'comment': event.comment or "",
                'tags': event.tags or "",
            }
        })


def _add_repetitive_occurrence_if_in_range(event, occurrence_dt, start_dt, end_dt, event_list):
    """
    Добавляет одну «итерацию» повторяющегося события (occurrence), если она
    попадает в диапазон [start_dt, end_dt].
    """
    start_event = occurrence_dt
    if event.duration and event.duration > 0:
        end_event = start_event + timedelta(minutes=event.duration)
    else:
        end_event = start_event

    # Проверяем пересечение с запрошенным диапазоном
    if end_event >= start_dt and start_event <= end_dt:
        event_list.append({
            'id': event.id,
            'title': event.name,
            'url': f"/money_event/{event.id}/",
            'class': 'income' if (event.amount and event.amount >= 0) else 'expense',
            'start': start_event.isoformat(),
            'end': end_event.isoformat(),
            'extendedProps': {
                'comment': event.comment or "",
                'tags': event.tags or "",
            }
        })


def parse_days_of_week(days_of_week_str):
    """
    Разбирает строку вида "0,2,4" в множество чисел {0,2,4},
    где 0=Понедельник, 6=Воскресенье (см. datetime.weekday()).
    Если строка пустая, вернёт пустое множество.
    """
    if not days_of_week_str:
        return set()
    # Разбиваем по запятой и преобразуем в int
    items = days_of_week_str.split(',')
    return set(int(x.strip()) for x in items if x.strip().isdigit())


def parse_specific_dates(dates_str):
    """
    Разбирает строку вида "2025-01-15,2025-01-20" в список date-объектов.
    Если строка пуста или формат неверный, возвращает пустой список.
    """
    if not dates_str:
        return []
    result = []
    items = dates_str.split(',')
    for item in items:
        item = item.strip()
        if not item:
            continue
        try:
            # Допустим формат "YYYY-MM-DD"
            parsed_date = datetime.strptime(item, '%Y-%m-%d').date()
            result.append(parsed_date)
        except ValueError:
            # Формат неверный — пропускаем
            pass
    return result
