from datetime import datetime, timedelta, time
from .models import MoneyEvent, RepetitiveType
from my_crm.weekdays import Weekday
from django.utils import timezone
from django.db.models import Q

def parse_days_of_week(days_of_week_str):
    """
    Разбирает строку вида "понедельник, Wednesday, 5" в множество чисел {1, 3, 5},
    где 1 = Понедельник, ... 7 = Воскресенье.
    """
    if not days_of_week_str:
        return set()
    items = days_of_week_str.split(',')
    return {Weekday.get_day_number(item.strip()) for item in items if item.strip()}

def parse_specific_dates(dates_str):
    """ Разбирает строку вида "2025-01-15,2025-01-20" в список date-объектов. """
    if not dates_str:
        return []
    return [
        datetime.strptime(item.strip(), '%Y-%m-%d').date()
        for item in dates_str.split(',')
        if item.strip()
    ]

class RepetitiveEventInstance():
    """
    Класс, представляющий единичный экземпляр повторяющегося события (не сохраняется в БД).

    Создаётся «на лету» при генерации всех дат для повторяющегося события из модели MoneyEvent.
    Фактически является «виртуальным» или «развёрнутым» событием, которое внешне
    похоже на обычное одиночное событие (SingleEvent).

    Параметры
    ---------
    event_id : int
        Идентификатор «родительского» события в БД (MoneyEvent.id),
        чтобы при необходимости можно было узнать, к какому событию относится эта виртуальная копия.
    name : str
        Название события (аналог поля `name` из MoneyEvent).
    start_datetime : datetime
        Дата и время начала (сформированное с учётом логики повторения).
    end_datetime : datetime
        Дата и время окончания (например, start_datetime + duration).
    status : str
        Текущий статус события (например, 'incomplete', 'complete' и т.д.), отражающий состояние «родительского» события.
    amount : Decimal, optional
        Сумма дохода/расхода; может отсутствовать, если не денежное событие.
    account_id : int, optional
        Ссылка на счёт (Account.id), если нужно отразить к какому счёту относится событие.
    ... : ...
        Любые другие поля, которые есть в реальном MoneyEvent / SingleEvent
        и которые вы хотите отразить в виртуальном экземпляре (например, tags, comment и т.п.).

    Методы
    ------
    to_dict():
        Возвращает словарь с информацией об экземпляре,
        который можно легко отправить через JsonResponse или использовать в шаблонах.
    """

    def __init__(
        self,
        parent_event,  # Ссылка на объект RepetitiveEvent
        start_datetime
    ):
        self.parent_event = parent_event  # Сохраняем родительский объект
        self.id = parent_event.id  # ID родительского события
        self.name = parent_event.name
        self.status = parent_event.event_status
        self.amount = parent_event.amount
        self.account_id = parent_event.account_id
        self.single_event_date = start_datetime
        self.tags = parent_event.tags

    def to_dict(self):
        """Возвращает словарь с данными, готовый к JSON-сериализации."""
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "amount": float(self.amount) if self.amount else None,
            "account_id": self.account_id,
            "single_event_date": self.single_event_date.isoformat(),
           # "end_datetime": self.end_datetime.isoformat(),
          #  "tags": self.tags,
          #  "comment": self.comment,
        }

class MoneyEventHandler:
    """
    Отвечает за «сбор» (из БД) и «расширение» (повторяющиеся события -> много дат)
    всех событий, попадающих в диапазон [start_dt, end_dt].
    Возвращает их в виде списка словарей или FakeEvent-объектов.
    """
    def __init__(self, generation_range_start=None, generation_range_end=None):
        self.generation_range_start = generation_range_start or (timezone.now()-timedelta(days=30))
        self.generation_range_end = generation_range_end or (timezone.now()+timedelta(days=30))
        self.events = []  # сюда будем складывать FakeEvent

    def form_relevant_events_collection(self):
        """
        Основной метод:
        1) Извлекает события из БД (при желании можем сразу отфильтровать).
        2) Обрабатывает одиночные (single) и генерирует виртуальные повторяющиеся (repetitive).
        3) Возвращает список событий в заданном диапазоне.

        :return: list[dict] - список словарей, описывающих каждое событие.
        """
        # 1) Получаем все подходящие события
        relevant_events = self._get_all_relevant_events()
        print("релевант евентс:", relevant_events)


        # 2) Собираем их в результирующий список
        result = []

        for event in relevant_events:
            if event.is_repetitive:
                # Генерируем виртуальные повторения
                repetitive_occurrences = self._generate_repetitive_event_instances(event)
                # print(repetitive_occurrences)
                result.extend(repetitive_occurrences)
            else:
                # Одиночное событие – если оно «попадает» в нужный диапазон,
                # добавим в общий список
                result.append(event)

        return result

    def _get_all_relevant_events(self):
        """
        Выбираем из БД события, которые потенциально могут быть в диапазоне.
        """

        qs = MoneyEvent.objects.filter(
            Q(start_repetition_date__gte=self.generation_range_start,
              start_repetition_date__lte=self.generation_range_end) |
            Q(end_repetition_date__gte=self.generation_range_start,
              end_repetition_date__lte=self.generation_range_end) |
            Q(single_event_date__gte=self.generation_range_start, single_event_date__lte=self.generation_range_end)
        )

        return qs

    def _generate_repetitive_event_instances(self, repetitive_event: MoneyEvent):
        """
        Генерирует экземпляры повторяющихся событий на основе настроек `repetitive_event`.

        Этот метод перебирает даты в диапазоне `generation_range_start` → `generation_range_end`
        и создаёт экземпляры событий, если они соответствуют условиям повторения.

        Варианты повторений:
        - **DAYS_OF_WEEK** → событие повторяется в определённые дни недели.
        - **VERY_DATE** → событие повторяется в конкретные даты месяца.
        - **N_DAYS** → событие повторяется через каждые X дней.

        Возвращает список экземпляров `RepetitiveEventInstance`, представляющих разовые повторения.

        :param repetitive_event: MoneyEvent, указывающий на повторяющееся событие.
        :return: list[RepetitiveEventInstance] - список созданных экземпляров событий.
        """

        print("репетатив ивент в генерации: ", repetitive_event)
        print("тип повторения: ", repetitive_event.repetitive_type)
        print("выбранные дни недели", repetitive_event.repetition_days_of_week)
        print(parse_days_of_week(repetitive_event.repetition_days_of_week))

        repetitions = []
        iteration_date = self.generation_range_start  # Начинаем с даты начала генерации событий

        # Если повторение по дням недели
        if repetitive_event.repetitive_type == RepetitiveType.DAYS_OF_WEEK:
            while iteration_date.date() <= self.generation_range_end:
                if iteration_date.isoweekday() in parse_days_of_week(repetitive_event.repetition_days_of_week):
                    repetitions.append(self._create_instance(repetitive_event, iteration_date))
                iteration_date += timedelta(days=1)

        # Если повторение по конкретным датам месяца
        elif repetitive_event.repetitive_type == RepetitiveType.VERY_DATE:
            specific_dates = parse_specific_dates(repetitive_event.repetition_dates_of_month)
            for specific_date in specific_dates:
                if self.generation_range_start <= specific_date <= self.generation_range_end:
                    repetitions.append(self._create_instance(repetitive_event, specific_date))

        # Если повторение через несколько дней
        elif repetitive_event.repetitive_type == RepetitiveType.N_DAYS:
            iteration_date = repetitive_event.start_repetition_date
            while iteration_date <= self.generation_range_end:
                if iteration_date >= self.generation_range_start:
                    repetitions.append(self._create_instance(repetitive_event, iteration_date))
                iteration_date += timedelta(days=repetitive_event.repetition_interval_days)

        return repetitions

    def _create_instance(self, repetitive_event: MoneyEvent, event_date):
        """
        Создаёт RepetitiveEventInstance для конкретного повторения события.
        """

        return MoneyEvent(
            parent=repetitive_event,
            single_event_date=event_date
        )
