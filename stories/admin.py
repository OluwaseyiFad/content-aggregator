from django.contrib import admin

from .models import Story, StoryChapter, StoryComment, StoryLike


class StoryChapterInline(admin.TabularInline):
    model = StoryChapter
    extra = 0


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'genre', 'word_count', 'reading_time', 'is_published', 'is_featured')
    list_filter = ('genre', 'is_published', 'is_featured', 'created_at')
    search_fields = ('title', 'summary', 'body', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('word_count', 'reading_time', 'created_at', 'updated_at')
    inlines = [StoryChapterInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'summary', 'body', 'cover_image')
        }),
        ('Metadata', {
            'fields': ('genre', 'word_count', 'reading_time')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return self.readonly_fields
        return self.readonly_fields + ('author',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'author' and not request.user.is_superuser:
            kwargs['initial'] = request.user.id
            kwargs['disabled'] = True
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(StoryChapter)
class StoryChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'story', 'order', 'word_count')
    list_filter = ('story',)
    search_fields = ('title', 'body')
    readonly_fields = ('word_count',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(story__author=request.user)


@admin.register(StoryComment)
class StoryCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'story', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'body')
    actions = ['approve_comments', 'reject_comments']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(story__author=request.user)

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(StoryLike)
class StoryLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'story', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'story__title')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(story__author=request.user)
