from django.contrib import admin

from .models import (
    BlogPost, ImageGallery, GalleryImage, ProgressBoard,
    ProgressColumn, ProgressCard, CodeSnippet, BlogComment
)


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1


class ImageGalleryInline(admin.TabularInline):
    model = ImageGallery
    extra = 0


class CodeSnippetInline(admin.TabularInline):
    model = CodeSnippet
    extra = 0


class ProgressColumnInline(admin.TabularInline):
    model = ProgressColumn
    extra = 0


class ProgressCardInline(admin.TabularInline):
    model = ProgressCard
    extra = 0


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_published', 'is_featured', 'published_at', 'created_at')
    list_filter = ('is_published', 'is_featured', 'created_at')
    search_fields = ('title', 'body', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ImageGalleryInline, CodeSnippetInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'excerpt', 'body', 'featured_image')
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


@admin.register(ImageGallery)
class ImageGalleryAdmin(admin.ModelAdmin):
    list_display = ('title', 'post', 'image_count')
    search_fields = ('title', 'post__title')
    inlines = [GalleryImageInline]

    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = 'Images'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(post__author=request.user)


@admin.register(ProgressBoard)
class ProgressBoardAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'is_public', 'updated_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('title', 'author__username')
    inlines = [ProgressColumnInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(ProgressColumn)
class ProgressColumnAdmin(admin.ModelAdmin):
    list_display = ('title', 'board', 'order', 'color')
    list_filter = ('board',)
    inlines = [ProgressCardInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(board__author=request.user)


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'body')
    actions = ['approve_comments', 'reject_comments']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(post__author=request.user)

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
