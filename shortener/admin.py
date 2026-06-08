from django.contrib import admin
from .models import URL, Click


@admin.register(URL)
class URLAdmin(admin.ModelAdmin):
    list_display = ("short_code", "user", "click_count", "created_at")
    list_filter = ("custom_code", "created_at")
    search_fields = ("short_code", "original_url", "user_username")


@admin.register(Click)
class ClickAdmin(admin.ModelAdmin):
    list_display = ("url", "clicked_at", "ip_address", "referrer")
    list_filter = ("clicked_at",)
    search_fields = ("url_short_code", "ip_address")
