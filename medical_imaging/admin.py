from django.contrib import admin

from .models import (
    MedicalImagingContent, MedicalImagingArticle,
    ArticleImage, ArticleComment
)


@admin.register(MedicalImagingContent)
class MedicalImagingContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'content_name', 'pub_date', 'has_image')
    list_filter = ('content_name', 'pub_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'pub_date'
    ordering = ('-pub_date',)

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = 'Image'


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1


@admin.register(MedicalImagingArticle)
class MedicalImagingArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'primary_topic', 'status', 'is_featured', 'published_at')
    list_filter = ('status', 'primary_topic', 'is_featured', 'created_at')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ArticleImageInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'summary', 'body', 'featured_image')
        }),
        ('Categorization', {
            'fields': ('primary_topic', 'status', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_description',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('published_at', 'created_at', 'updated_at'),
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


@admin.register(ArticleComment)
class ArticleCommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created_at', 'is_approved')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('author__username', 'body')
    actions = ['approve_comments', 'reject_comments']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(article__author=request.user)

    @admin.action(description='Approve selected comments')
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description='Reject selected comments')
    def reject_comments(self, request, queryset):
        queryset.update(is_approved=False)
