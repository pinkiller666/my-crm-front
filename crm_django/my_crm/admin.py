from django.contrib import admin
from .models import Account, Event, EventInstance, Artist, AcceptedCommission


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


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(AcceptedCommission)
class AcceptedCommissionAdmin(admin.ModelAdmin):
    list_display = ("artist", "amount", "accepted_at", "comment")
    list_filter = (MonthYearFilter, "artist")  # ← добавили сюда!
    search_fields = ("artist__name", "comment")
    date_hierarchy = "accepted_at"
