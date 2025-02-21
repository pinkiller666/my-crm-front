# forms.py
from django import forms
from datetime import date, timedelta
from .models import MoneyEvent, Account, RepetitiveType

class MoneyEventForm(forms.ModelForm):
    """Форма для создания/редактирования события с учётом новых полей модели."""

    # Дополнительные поля, которых нет прямо в модели, но они нужны пользователю
    event_type = forms.ChoiceField(
        choices=[
            ('single', 'Одноразовое событие'),
            ('repetitive', 'Повторяющееся событие'),
        ],
        required=True,
        widget=forms.RadioSelect
    )

    repetition_type = forms.ChoiceField(
        choices=[
            ('weekdays', 'По дням недели'),
            ('dates', 'По конкретным датам'),
            ('interval', 'Через каждые X дней'),
        ],
        required=False,
        widget=forms.RadioSelect
    )

    # Для списка дней недели
    repetition_days_of_week = forms.CharField(required=False)

    # Для дат (1, 15 ...) и интервала
    repetition_dates_of_month = forms.CharField(required=False)
    repetition_interval_days = forms.IntegerField(required=False, min_value=1)

    # Выбор аккаунта
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=True,
        label="Принадлежность бюджета"
    )

    # Теги, записываемые в одну строку
    tags = forms.CharField(required=False)

    # Флажок "На 4 месяца"
    auto_four_months = forms.BooleanField(required=False)

    class Meta:
        model = MoneyEvent
        fields = [
            'event_type',
            'name',
            'amount',
            'comment',
            'account',
            'tags',

            # Для одноразового события
            'single_event_date',

            # Для повторяющегося события
            'repetition_type',
            'repetition_days_of_week',
            'repetition_dates_of_month',
            'repetition_interval_days',

            'start_repetition_date',
            'end_repetition_date',

            # Время выполнения события
            'doing_start_time',
            'doing_duration_time',
            'doing_end_time',

            'auto_four_months',
        ]
        # Не указываем event_status и event_is_active — они устанавливаются в `save()`.

    def clean(self):
        """Валидация данных перед сохранением."""
        cleaned_data = super().clean()

        # Проверяем, если выбрано повторяющееся событие
        if cleaned_data.get('event_type') == 'repetitive':
            rep_type = cleaned_data.get('repetition_type')
            if not rep_type:
                self.add_error('repetition_type', 'Выберите тип повторения')

        return cleaned_data

    def save(self, commit=True):
        """Обрабатываем сохранение формы с учётом типа события."""
        instance: MoneyEvent = super().save(commit=False)

        # event_type -> is_repetitive
        event_type = self.cleaned_data.get('event_type')
        if event_type == 'single':
            instance.is_repetitive = False
            instance.repetitive_type = None
            instance.repetition_interval_days = 0
            instance.repetition_dates_of_month = ""
            instance.repetition_days_of_week = ""
        else:
            # Повторяющееся событие
            instance.is_repetitive = True
            rep_type = self.cleaned_data.get('repetition_type')

            if rep_type == 'weekdays':
                instance.repetitive_type = RepetitiveType.DAYS_OF_WEEK.value
                instance.repetition_days_of_week = self.cleaned_data.get('repetition_days_of_week', "")
                instance.repetition_dates_of_month = ""
                instance.repetition_interval_days = 0
            elif rep_type == 'dates':
                instance.repetitive_type = RepetitiveType.VERY_DATE.value
                instance.repetition_dates_of_month = self.cleaned_data.get('repetition_dates_of_month', "")
                instance.repetition_days_of_week = ""
                instance.repetition_interval_days = 0
            elif rep_type == 'interval':
                instance.repetitive_type = RepetitiveType.N_DAYS.value
                instance.repetition_interval_days = self.cleaned_data.get('repetition_interval_days') or 0
                instance.repetition_days_of_week = ""
                instance.repetition_dates_of_month = ""
            else:
                instance.repetitive_type = None  # На случай ошибок

        # Если выставлен "На 4 месяца", корректируем `end_repetition_date`
        if self.cleaned_data.get('auto_four_months'):
            instance.end_repetition_date = instance.start_repetition_date + timedelta(days=120)

        # Устанавливаем статус по умолчанию
        if not instance.event_status:
            instance.event_status = 'incomplete'

        # Сохраняем объект
        if commit:
            instance.save()
        return instance
