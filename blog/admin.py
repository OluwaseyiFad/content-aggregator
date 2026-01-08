from django.contrib import admin
from django.utils import timezone

from .models import (
    GeneralContent, PythonContent, CyberSecurityContent,
    SoftwareDevelopmentContent, UiUxContent, MobilePcContent,
    JobUpdatesContent, CryptoContent, RSSFeed, UserBookmark
)


class BaseContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_name', 'pub_date', 'has_image')
    list_filter = ('content_name', 'pub_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'


@admin.register(GeneralContent)
class GeneralContentAdmin(BaseContentAdmin):
    pass


@admin.register(PythonContent)
class PythonContentAdmin(BaseContentAdmin):
    pass


@admin.register(CyberSecurityContent)
class CyberSecurityContentAdmin(BaseContentAdmin):
    pass


@admin.register(SoftwareDevelopmentContent)
class SoftwareDevelopmentContentAdmin(BaseContentAdmin):
    pass


@admin.register(UiUxContent)
class UiUxContentAdmin(BaseContentAdmin):
    pass


@admin.register(MobilePcContent)
class MobilePcContentAdmin(BaseContentAdmin):
    pass


@admin.register(JobUpdatesContent)
class JobUpdatesContentAdmin(BaseContentAdmin):
    pass


@admin.register(CryptoContent)
class CryptoContentAdmin(BaseContentAdmin):
    pass


@admin.register(RSSFeed)
class RSSFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active', 'last_fetched', 'has_error')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'url')
    readonly_fields = ('last_fetched', 'fetch_error', 'created_at')
    actions = ['activate_feeds', 'deactivate_feeds', 'clear_errors']

    def has_error(self, obj):
        return bool(obj.fetch_error)
    has_error.boolean = True
    has_error.short_description = 'Error'

    @admin.action(description='Activate selected feeds')
    def activate_feeds(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected feeds')
    def deactivate_feeds(self, request, queryset):
        queryset.update(is_active=False)

    @admin.action(description='Clear fetch errors')
    def clear_errors(self, request, queryset):
        queryset.update(fetch_error='')


@admin.register(UserBookmark)
class UserBookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'content_type', 'is_read', 'created_at')
    list_filter = ('content_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title')
    readonly_fields = ('created_at',)
