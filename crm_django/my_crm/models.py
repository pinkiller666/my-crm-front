from decimal import Decimal
from django.db import models
from django.utils import timezone
from recurrence.fields import RecurrenceField

# Выбираем TextChoices, чтобы хранить строки (аналог value в Enum)
class CompletionStatus(models.TextChoices):
    INCOMPLETE = 'incomplete', 'INCOMPLETE'
    COMPLETE = 'complete', 'COMPLETE'
    CANCELLED = 'cancelled', 'CANCELLED'
    ON_PAUSE = 'on_pause', 'ON_PAUSE'
    IN_PROCESS = 'in_process', 'IN_PROCESS'

def one_year_from_now():
    return timezone.now().date().replace(year=timezone.now().year + 1)


class Account(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name





class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,  # NULL означает не денежное событие
        blank=True,
        default=Decimal('-0.01')  # По умолчанию считается тратой
    )
    account = models.ForeignKey(
        Account,
        related_name='events',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    recurrence = RecurrenceField(blank=True, null=True, include_dtstart=False)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
            max_length=50,
            choices=CompletionStatus.choices,
            default=CompletionStatus.INCOMPLETE
    )

    def __str__(self):
        return self.name


class EventInstance(models.Model):
        """Хранит изменения фейковых событий (экземпляров)"""
        parent_event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='instances')
        instance_datetime = models.DateTimeField()  # Дата и время конкретного экземпляра
        status = models.CharField(
            max_length=50,
            choices=CompletionStatus.choices,
            default=CompletionStatus.INCOMPLETE
        )
        modified_at = models.DateTimeField(auto_now=True)  # Когда изменялось

        def __str__(self):
            return f"{self.parent_event.name} ({self.instance_datetime.strftime('%Y-%m-%d %H:%M')})"


class Artist(models.Model):
    name = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name


class AcceptedCommission(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="commissions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_at = models.DateField(auto_now_add=True)
    comment = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.artist.name} — {self.amount} ₽ — {self.accepted_at}"

class MonthGoal(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    goal = models.IntegerField(null=False, default=10000)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['year', 'month'], name='unique_month_goal')
        ]