from datetime import date
from decimal import Decimal
from django.db import models
from django.utils import timezone
from recurrence.fields import RecurrenceField
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError


class User(AbstractUser):
    role = models.CharField(max_length=50)

    def __str__(self):
        roles = []
        if hasattr(self, 'as_artist'):
            roles.append('🎨 artist')
        if hasattr(self, 'as_manager'):
            roles.append('📋 manager')
        if hasattr(self, 'as_middleman'):
            roles.append('💸 middleman')

        role_display = ', '.join(roles) if roles else '👤 user'
        return f"{self.username} ({role_display})"


def current_year():
    return date.today().year


def current_month():
    return date.today().month


class CompletionStatus(models.TextChoices):
    INCOMPLETE = 'incomplete', 'INCOMPLETE'
    COMPLETE = 'complete', 'COMPLETE'
    CANCELLED = 'cancelled', 'CANCELLED'
    ON_PAUSE = 'on_pause', 'ON_PAUSE'
    IN_PROCESS = 'in_process', 'IN_PROCESS'


class DayType(models.TextChoices):
    WORK = 'work', 'Рабочий'
    OFF = 'off', 'Выходной'
    HOLIDAY = 'holiday', 'Праздник'
    VACATION = 'vacation', 'Отпуск'
    TASK = 'task', 'Дело'


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
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=Decimal('-0.01'))
    account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    recurrence = RecurrenceField(blank=True, null=True, include_dtstart=False)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    tags = models.JSONField(default=list, blank=True)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=CompletionStatus.choices, default=CompletionStatus.INCOMPLETE)
    is_task = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class EventInstance(models.Model):
    parent_event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='instances')
    instance_datetime = models.DateTimeField()
    status = models.CharField(max_length=50, choices=CompletionStatus.choices, default=CompletionStatus.INCOMPLETE)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.parent_event.name} ({self.instance_datetime.strftime('%Y-%m-%d %H:%M')})"


class MonthGoal(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    goal = models.IntegerField(null=False, default=10000)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['year', 'month'], name='unique_month_goal')]


class Manager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='as_manager', null=True, blank=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Middleman(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='as_middleman', null=True, blank=True)
    name = models.CharField(max_length=255)
    percent = models.DecimalField(max_digits=5, decimal_places=2)
    paypal_address = models.CharField(max_length=70)

    def __str__(self):
        return f"{self.name} ({self.percent}%)"


class Artist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='as_artist', null=True, blank=True)
    name = models.CharField(max_length=255)
    manager = models.ForeignKey(Manager, on_delete=models.CASCADE, related_name="artists")

    def __str__(self):
        return self.name


class Slot(models.Model):
    date_range = models.DateTimeField()
    status = models.CharField(max_length=255, choices=[('available', 'Available'), ('booked', 'Booked')])

    def __str__(self):
        return f"Slot {self.date_range} - {self.status}"


class Order(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('completed', 'Completed'), ('cancelled', 'Cancelled')]

    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    description = models.TextField()
    type = models.CharField(max_length=255)
    slot = models.ForeignKey(Slot, null=True, blank=True, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)

    def __str__(self):
        return f"Order by {self.client.name} with {self.artist.name}"


class Payment(models.Model):
    PAY_SYSTEM_CHOICES = [('paypal', 'PayPal'), ('bank_transfer', 'Bank Transfer')]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    middleman = models.ForeignKey(Middleman, on_delete=models.SET_NULL, null=True, blank=True)
    currency = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    pay_system = models.CharField(max_length=50, choices=PAY_SYSTEM_CHOICES)

    def __str__(self):
        return f"Payment for {self.order}, {self.amount} {self.currency}"


class PriceEntry(models.Model):
    artist = models.ForeignKey(Artist, related_name='pricelist', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='pricelist/', null=True, blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])])

    def __str__(self):
        if self.title:
            return self.title
        elif self.image:
            return f'Изображение для {self.artist.name}'
        return f'Пустая запись ({self.artist.name})'


class Payout(models.Model):
    PAYOUT_STATUS_CHOICES = [('pending', 'Pending'), ('paid', 'Paid')]

    middleman = models.ForeignKey(Middleman, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="payouts")
    orders = models.ManyToManyField(Order)
    status = models.CharField(max_length=50, choices=PAYOUT_STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payments = models.ManyToManyField(Payment)

    def __str__(self):
        return f"Payout {self.status} for {self.artist.name} of {self.amount} {self.orders.count()} orders"


class AcceptedCommission(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name="commissions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_at = models.DateField(auto_now_add=True)
    comment = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f"{self.artist.name} — {self.amount} ₽ — {self.accepted_at}"


class SchedulePattern(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    days_off_at_start = models.PositiveSmallIntegerField(default=0)
    pattern_after_start = models.JSONField(default=list)
    last_day_always_working = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = '📅 Расписание — Шаблоны'

    def __str__(self):
        return self.name


class MonthSchedule(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=current_year)
    month = models.PositiveSmallIntegerField(default=current_month)
    pattern = models.ForeignKey(SchedulePattern, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('user', 'year', 'month')
        verbose_name_plural = '📅 Расписание — Назначенные шаблоны'

    def __str__(self):
        return f"{self.user.username} — {self.year}-{self.month:02d}: {self.pattern.name}"


class DayOverride(models.Model):
    month_schedule = models.ForeignKey(MonthSchedule, on_delete=models.CASCADE, related_name="overrides")
    date = models.DateField()
    type = models.CharField(max_length=20, choices=DayType.choices, default=DayType.OFF)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = '📅 Расписание — Исключения'
        constraints = [models.UniqueConstraint(fields=['month_schedule', 'date'], name='unique_day_per_monthschedule')]

    def __str__(self):
        return f"{self.date}: {self.type}"


class Task(Event):
    class CategoryChoices(models.TextChoices):
        WORK = 'work', 'Рабочее'
        LIFE = 'life', 'Пожизневые'
        SPORT = 'sport', 'Спорт'
        MEDICAL = 'medical', 'Медицина'

    class TypeChoices(models.TextChoices):
        FUN = 'fun', 'Кайфовые'
        ROUTINE = 'routine', 'Рутина'
        IMPORTANT = 'important', 'Важные'
        HEAVY = 'heavy', 'Трудоемкие'
        GROSS = 'gross', 'Мерзкие'

    body = models.TextField(blank=True)
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    date_day = models.DateField()
    category = models.CharField(max_length=32, choices=CategoryChoices.choices, blank=True, null=True)
    type = models.CharField(max_length=32, choices=TypeChoices.choices, blank=True, null=True)

    def clean(self):
        super().clean()
        if self.start_hour is not None and self.start_minute is not None and self.end_hour is not None and self.end_minute is not None:
            start_total = self.start_hour * 60 + self.start_minute
            end_total = self.end_hour * 60 + self.end_minute
            if end_total <= start_total:
                raise ValidationError("Время окончания должно быть позже времени начала.")

    def save(self, *args, **kwargs):
        self.is_task = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.date_day})"
