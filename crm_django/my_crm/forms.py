# forms.py
from django import forms
from datetime import date, timedelta
from .models import MoneyEvent, Account, RepetitiveType

class MoneyEventForm(forms.ModelForm):
    """Форма для создания/редактирования события в стиле Django + дополнительная логика."""

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

    # Для списка дней недели в форме можно использовать CheckboxSelectMultiple
    # но мы сделаем CharField, чтобы собрать это из JS:
    weekdays = forms.CharField(required=False)

    # Для дат (1, 15 ...) и интервала
    repetitive_dates = forms.CharField(required=False)
    repetitive_interval = forms.IntegerField(required=False, min_value=1)

    # Чтобы выбрать аккаунт, используем ModelChoiceField
    account = forms.ModelChoiceField(
        queryset=Account.objects.all(),
        required=True,
        label="Принадлежность бюджета"
    )

    # Хэштеги соберём в одну строку, как у вас в модели (tags = TextField),
    # но пользователь может добавлять «стандартные» и «кастомные» хэштеги
    # см. в шаблоне, как это обрабатываем с JS
    # Здесь в форме поле tags будет скрытым или обычным TextField
    tags = forms.CharField(required=False)

    # "На 4 месяца" флажок
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
            'event_date',

            # Для повторяющегося события
            'repetition_type',
            'weekdays',
            'repetitive_dates',
            'repetitive_interval',

            'start_date',
            'end_date',

            'auto_four_months',
        ]
        # Тут не указываем status, is_repetitive, repetitive_type напрямую —
        # они будут установлены в методе save() или clean().

    def clean(self):
        cleaned_data = super().clean()

        # Если выбрано повторяющееся событие
        if cleaned_data.get('event_type') == 'repetitive':
            # Тогда убедимся, что repetition_type заполнен
            rep_type = cleaned_data.get('repetition_type')
            if not rep_type:
                self.add_error('repetition_type', 'Выберите тип повторения')

        return cleaned_data

    def save(self, commit=True):
        """Переопределяем save, чтобы заполнить поля модели
        в соответствии с выбранным типом события."""
        instance: MoneyEvent = super().save(commit=False)

        # event_type -> is_repetitive
        event_type = self.cleaned_data.get('event_type')
        if event_type == 'single':
            instance.is_repetitive = False
            # На всякий случай, чтобы не засорять
            instance.repetitive_type = None
            instance.n_days = 0
            instance.dates = ""
            instance.days_of_week = ""
        else:
            # repetitive
            instance.is_repetitive = True
            rep_type = self.cleaned_data.get('repetition_type')

            if rep_type == 'weekdays':
                instance.repetitive_type = RepetitiveType.DAYS_OF_WEEK.value
                # из формы weekdays (например, "Понедельник,Вторник")
                instance.days_of_week = self.cleaned_data.get('weekdays', "")
                instance.dates = ""
                instance.n_days = 0
            elif rep_type == 'dates':
                instance.repetitive_type = RepetitiveType.VERY_DATE.value
                instance.dates = self.cleaned_data.get('repetitive_dates', "")
                instance.days_of_week = ""
                instance.n_days = 0
            elif rep_type == 'interval':
                instance.repetitive_type = RepetitiveType.N_DAYS.value
                instance.n_days = self.cleaned_data.get('repetitive_interval') or 0
                instance.days_of_week = ""
                instance.dates = ""
            else:
                instance.repetitive_type = None  # неизвестный, но теоретически не должно быть

        # Если выставлен "На 4 месяца" - можно автокорректировать end_date
        if self.cleaned_data.get('auto_four_months'):
            instance.end_date = instance.start_date + timedelta(days=120)

        # status по умолчанию: incomplete (если в модели не стоит default, зададим)
        if not instance.status:
            instance.status = 'incomplete'

        # Сохраняем (commit=True) и возвращаем объект
        if commit:
            instance.save()
        return instance
