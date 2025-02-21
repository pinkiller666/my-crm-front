from decimal import Decimal
from django.db import models
from django.utils import timezone
from recurrence.fields import RecurrenceField


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
        choices=[
            ('incomplete', 'Incomplete'),
            ('complete', 'Complete'),
            ('cancelled', 'Cancelled')
        ],
        default='incomplete'
    )

    def __str__(self):
        return self.name
