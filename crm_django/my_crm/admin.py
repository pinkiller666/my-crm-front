from django.contrib import admin
from .models import Account, Event, EventInstance, AcceptedCommission, SchedulePattern, MonthSchedule, DayOverride, User
from .models import Manager, Artist, Client, Order, Slot, Payment, Middleman, Payout, PriceEntry
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import Task

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "balance", "is_archived",
                    "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_archived",)
    ordering = ("-created_at",)


@admin.register(EventInstance)
class EventInstanceAdmin(admin.ModelAdmin):
    list_display = ("parent_event", "instance_datetime", "status",
                    "modified_at")
    list_filter = ("status",)
    ordering = ("-modified_at",)

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "amount", "account",
                    "start_datetime", "status", "is_active")
    search_fields = ("name", "description", "account__name")
    list_filter = ("is_active", "status")
    ordering = ("-start_datetime",)
    filter_horizontal = ()
    fieldsets = (
        ("General", {
            "fields": ("name", "description", "amount", "account", "tags", "comment")
        }),
        ("Time & Recurrence", {
            "fields": ("start_datetime", "end_datetime", "duration_minutes", "recurrence")
        }),
        ("Status & Metadata", {
            "fields": ("is_active", "status", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    readonly_fields = ("created_at", "updated_at")

class MonthYearFilter(admin.SimpleListFilter):
    title = "месяц и год"
    parameter_name = "month_year"

    def lookups(self, request, model_admin):
        dates = AcceptedCommission.objects.dates("accepted_at", "month", order="DESC")
        return [(date.strftime("%Y-%m"), date.strftime("%B %Y")) for date in dates]

    def queryset(self, request, queryset):
        if self.value():
            year, month = map(int, self.value().split("-"))
            return queryset.filter(accepted_at__year=year, accepted_at__month=month)
        return queryset

@admin.register(AcceptedCommission)
class AcceptedCommissionAdmin(admin.ModelAdmin):
    list_display = ("artist", "amount", "accepted_at", "comment")
    list_filter = (MonthYearFilter, "artist")  # ← добавили сюда!
    search_fields = ("artist__name", "comment")
    date_hierarchy = "accepted_at"


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0  # No extra empty fields
    readonly_fields = ('amount', 'currency', 'pay_system')


# Order Admin with inline Payments
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'artist', 'status', 'type', 'slot', 'date')
    list_filter = ('status', 'artist', 'client')
    search_fields = ('client__name', 'artist__name', 'description')
    inlines = [PaymentInline]
    readonly_fields = ('slot',)  # Prevent editing slots once set


# Slot Admin to manage available/booked slots
class SlotAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_range', 'status')
    list_filter = ('status',)
    search_fields = ('date_range',)


# Inline form to add/edit PriceEntry items within the Artist admin page
class PriceEntryInline(admin.TabularInline):
    model = PriceEntry
    extra = 1  # Shows 1 extra blank form for adding new entries
    fields = ('title', 'image')
    min_num = 0
    max_num = 10  # Set a limit on the maximum number of price entries if needed


# Artist Admin with Inline Price List
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'manager')
    list_filter = ('manager',)
    search_fields = ('name',)
    inlines = [PriceEntryInline]  # Add inline for managing the price list

# Middleman Admin


class MiddlemanAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'percent')
    search_fields = ('name',)


# Payment Admin
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'middleman',
                    'amount', 'currency', 'pay_system')
    list_filter = ('pay_system', 'middleman')
    search_fields = ('order__client__name',
                     'order__artist__name', 'middleman__name')


# Payout Admin
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'middleman', 'artist', 'status', 'amount')
    list_filter = ('status', 'middleman', 'artist')
    search_fields = ('middleman__name', 'artist__name')
    # Adds filtering widget for many-to-many fields
    filter_horizontal = ('orders', 'payments')

    def total_orders(self, obj):
        return obj.orders.count()
    total_orders.short_description = "Total Orders"


# Manager Admin
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# Client Admin
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'get_roles', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('is_staff', 'is_active')

    def get_roles(self, obj):
        roles = []
        if hasattr(obj, 'as_artist'):
            roles.append('🎨')
        if hasattr(obj, 'as_manager'):
            roles.append('📋')
        if hasattr(obj, 'as_middleman'):
            roles.append('💸')
        return ' '.join(roles) or '—'

    get_roles.short_description = 'Роли'




@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_day', 'user', 'category', 'type', 'is_active')
    list_filter = ('category', 'type', 'user')
    search_fields = ('title', 'body', 'comment')
    ordering = ('-date_day',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'user', 'date_day', 'category', 'type'),
        }),
        ('Описание', {
            'fields': ('body', 'comment'),
        }),
        ('Поведение события', {
            'fields': ('start_datetime', 'end_datetime', 'duration_minutes', 'tags', 'status'),
        }),
        ('Финансы', {
            'fields': ('amount', 'account'),
        }),
        ('Дополнительно', {
            'fields': ('recurrence', 'is_active'),
        }),
    )


# Register all models with their customized admin views
admin.site.register(Manager, ManagerAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Slot, SlotAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Middleman, MiddlemanAdmin)
admin.site.register(Payout, PayoutAdmin)
admin.site.register(SchedulePattern)
admin.site.register(MonthSchedule)
admin.site.register(DayOverride)


