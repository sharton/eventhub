from django.contrib import admin
from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'starts_at', 'is_published', 'is_deleted')
    list_filter = ('is_published', 'is_deleted')
    search_fields = ('title', 'summary')