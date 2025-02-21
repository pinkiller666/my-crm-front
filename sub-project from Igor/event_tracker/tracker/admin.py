from django.contrib import admin
from .models import Account, Event


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("name", "balance", "is_archived",
                    "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_archived",)
    ordering = ("-created_at",)


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
