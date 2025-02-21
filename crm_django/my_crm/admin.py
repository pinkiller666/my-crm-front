from django.contrib import admin
from .models import Account, MoneyEvent


class ParentFilter(admin.SimpleListFilter):
    title = "Has Parent"
    parameter_name = "has_parent"

    def lookups(self, request, model_admin):
        return [
            ("yes", "With Parent"),
            ("no", "Without Parent"),
        ]

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.exclude(parent__isnull=True)  # Only with parent
        elif self.value() == "no":
            return queryset.filter(parent__isnull=True)  # Only without parent
        return queryset

class MoneyEventInline(admin.TabularInline):
    """Вложенное отображение событий в аккаунте."""
    model = MoneyEvent
    extra = 1  # Количество пустых форм для добавления в inline


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    """Настройки отображения аккаунтов в админке."""
    list_display = ('name', 'description', 'current_amount', 'is_old')
    inlines = [MoneyEventInline]  # Вложенные события MoneyEvent внутри аккаунта


@admin.register(MoneyEvent)
class MoneyEventAdmin(admin.ModelAdmin):
    """Настройки отображения событий в админке."""

    # Отображаемые поля в списке объектов
    list_display = (
        'name', 'amount', 'event_status', 'account',
        'event_is_active', 'is_repetitive', 'single_event_date', 'updated_at_inner_info'
    )

    # Фильтры в правой части
    list_filter = ('event_status', 'event_is_active', 'is_repetitive', 'account', ParentFilter)

    # По каким полям доступен поиск
    search_fields = ('name', 'comment', 'tags')

    # Добавляет иерархию по дате (фильтрация по году, месяцу и дню)
    date_hierarchy = 'single_event_date'

    # Позволяет листать по 20 записей на странице
    list_per_page = 20

    # Поля, которые нельзя будет изменять (только для чтения)
    readonly_fields = ('created_at_inner_info', 'updated_at_inner_info', 'edited_at_inner_info')

    # Поля сгруппированы для удобного редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'amount', 'event_status', 'account', 'event_is_active', 'is_repetitive','single_event_date', 'parent')
        }),
        ('Настройки повторений', {
            'classes': ('collapse',),  # Сделает этот блок сворачиваемым
            'fields': (
                'repetitive_type', 'repetition_interval_days', 'repetition_dates_of_month',
                'repetition_days_of_week', 'start_repetition_date', 'end_repetition_date',
            ),
        }),
        ('Время выполнения', {
            'classes': ('collapse',),
            'fields': (
                'doing_start_time', 'doing_duration_time', 'doing_end_time',
            ),
        }),
        ('Дополнительная информация', {
            'classes': ('collapse',),
            'fields': (
                'comment', 'tags',
                ('created_at_inner_info', 'updated_at_inner_info'),
            ),
        }),
    )
