from django.contrib import admin
from .models import Client, Order


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "phone", "address")
    search_fields = ("first_name", "last_name", "phone")
    ordering = ("last_name", "first_name")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("client", "order_type", "assigned_to", "date", "time", "status")
    list_filter = ("status", "order_type", "date")
    search_fields = (
        "client__first_name",
        "client__last_name",
        "description",
        "assigned_to__username",
    )
    autocomplete_fields = ("client", "assigned_to")
    ordering = ("-date", "-time")
