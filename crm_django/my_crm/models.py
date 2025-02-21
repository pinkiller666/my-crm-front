from datetime import timedelta
from django.db import models
from django.utils import timezone
from decimal import Decimal


# Выбираем TextChoices, чтобы хранить строки (аналог value в Enum)
class CompletionStatus(models.TextChoices):
    INCOMPLETE = 'incomplete', 'INCOMPLETE'
    COMPLETE = 'complete', 'COMPLETE'
    CANCELLED = 'cancelled', 'CANCELLED'
    ON_PAUSE = 'on_pause', 'ON_PAUSE'
    IN_PROCESS = 'in_process', 'IN_PROCESS'


class RepetitiveType(models.TextChoices):
    DAYS_OF_WEEK = 'days_of_week', 'days_of_week'
    VERY_DATE = 'very_date', 'very_date'
    N_DAYS = 'n_days', 'n_days'


def one_year_from_now():
    return (timezone.now() + timedelta(days=365)).date()


class Account(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    current_amount = models.IntegerField(default=0)
    is_old = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class MoneyEvent(models.Model):
    repetitive_type = models.CharField(
        max_length=50,
        choices=RepetitiveType.choices,
        blank=True,
        null=True
    )

    # как повторяются
    is_repetitive = models.BooleanField(default=False)
    repetition_interval_days = models.IntegerField(blank=True, null=True)
    repetition_dates_of_month = models.CharField(max_length=255, default="", blank=True, null=True)
    repetition_days_of_week = models.CharField(max_length=255, default="", blank=True, null=True)

    # поля касающееся времени
        # даты
    single_event_date = models.DateTimeField(default=timezone.now)
    start_repetition_date = models.DateField(default=timezone.now, null=True, blank=True)   # дата начала
    end_repetition_date = models.DateField(default=one_year_from_now, blank=True, null=True)  # дата окончания
        # часы, время выполнения
    doing_start_time = models.TimeField(blank=True, null=True)
    doing_duration_time = models.IntegerField(default=0, null=True, blank=True)  # продолжительность в минутах
    doing_end_time = models.TimeField(blank=True, null=True)

    # описательные поля
    name = models.CharField(max_length=255, default="")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,  # NULL означает не денежное событие
        blank=True,
        default=Decimal("-0.01")  # Стандартное значение. Показывает что по умолчанию ивент = трата
    )
    comment = models.TextField(blank=True, null=True)
    tags = models.TextField(default="", blank=True)
    event_is_active = models.BooleanField(default=True)
    event_status = models.CharField(
        max_length=50,
        choices=CompletionStatus.choices,
        default=CompletionStatus.INCOMPLETE
    )

    account = models.ForeignKey(
        Account,
        related_name='money_events',
        on_delete=models.CASCADE,
        null=True,  # Разрешаем хранить NULL
        blank=True  # Разрешаем не заполнять в формах
    )

    # внутренние данные о записи
    created_at_inner_info = models.DateTimeField(default=timezone.now)
    edited_at_inner_info = models.DateTimeField(default=timezone.now)
    updated_at_inner_info = models.DateTimeField(default=timezone.now)

    parent = models.ForeignKey(
        "self",  # Self-referential foreign key
        on_delete=models.CASCADE,  # Deleting the parent removes all related instances
        related_name="children",  # Allows reverse access via parent.children.all()
        null=True,  # Allow null if it's the first event in a series
        blank=True
    )

    def __str__(self):
        return self.name
