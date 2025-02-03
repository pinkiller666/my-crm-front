from django.contrib import admin
from .models import Account, MoneyEvent

class MoneyEventInline(admin.TabularInline):
    model = MoneyEvent
    extra = 1  # Количество пустых форм для добавления в inline

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'current_amount', 'is_old')
    inlines = [MoneyEventInline]

@admin.register(MoneyEvent)
class MoneyEventAdmin(admin.ModelAdmin):
    # Отображаемые поля в списке объектов
    list_display = (
        'name', 'amount', 'status', 'account',
        'is_active', 'is_repetitive', 'event_date', 'updated_at'
    )
    # Фильтры в правой части
    list_filter = ('status', 'is_active', 'is_repetitive', 'account')
    # По каким полям доступен поиск
    search_fields = ('name', 'comment', 'tags')
    # Добавляет иерархию по дате (фильтрация по году, месяцу и дню)
    date_hierarchy = 'event_date'
    # Позволяет листать по 20 записей на странице (можешь настроить сам)
    list_per_page = 20
    # Поля, которые нельзя будет изменять (только для чтения)
    readonly_fields = ('created_at', 'edited_at', 'updated_at')
    # Можно сгруппировать поля в формы (опционально)
    fieldsets = (
        (None, {
            'fields': ('name', 'amount', 'status', 'account', 'is_active', 'is_repetitive')
        }),
        ('Расширенные настройки', {
            'classes': ('collapse',),  # Сделает этот блок сворачиваемым
            'fields': (
                'repetitive_type', 'n_days', 'dates', 'days_of_week',
                'start_date', 'end_date', 'comment', 'tags',
                'start_time', 'duration', 'end_time',
                ('created_at', 'edited_at', 'event_date', 'updated_at'),
            ),
        }),
    )

