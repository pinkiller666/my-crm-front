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
    n_days = models.IntegerField(blank=True, null=True)
    dates = models.CharField(max_length=255, default="", blank=True)
    days_of_week = models.CharField(max_length=255, default="", blank=True)
    start_date = models.DateField(default=timezone.now, null=True, blank=True)   # дата начала
    duration = models.IntegerField(default=0, null=True, blank=True)  # продолжительность в минутах
    end_date = models.DateField(default=one_year_from_now, blank=True, null=True)  # дата окончания
    is_active = models.BooleanField(default=True)
    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)
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
    is_repetitive = models.BooleanField(default=False)
    account = models.ForeignKey(
        Account,
        related_name='money_events',
        on_delete=models.CASCADE,
        null=True,  # Разрешаем хранить NULL
        blank=True  # Разрешаем не заполнять в формах
    )
    created_at = models.DateTimeField(default=timezone.now)
    edited_at = models.DateTimeField(default=timezone.now)
    event_date = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=50,
        choices=CompletionStatus.choices,
        default=CompletionStatus.INCOMPLETE
    )
