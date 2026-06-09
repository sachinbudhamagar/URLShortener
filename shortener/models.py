from django.db import models
from django.conf import settings


class URL(models.Model):
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=15, unique=True, db_index=True)
    custom_code = models.BooleanField(default=False)
    click_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="urls",
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.short_code} -> {self.original_url[:50]}"


class Click(models.Model):
    url = models.ForeignKey(URL, on_delete=models.CASCADE, related_name="clicks")
    clicked_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    referrer = models.URLField(max_length=2000, blank=True)

    class Meta:
        ordering = ["-clicked_at"]

    def __str__(self):
        return f"Click on {self.url.short_code} at {self.clicked_at}"
