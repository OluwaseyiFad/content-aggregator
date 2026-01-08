from django.contrib.auth.models import User
from django.db import models


class RSSFeed(models.Model):
    """Dynamic RSS feed management - replaces hardcoded feeds in tasks.py"""

    CATEGORY_CHOICES = [
        ('general', 'General Tech'),
        ('python', 'Python'),
        ('cybersecurity', 'Cyber Security'),
        ('software_dev', 'Software Development'),
        ('ui_ux', 'UI/UX'),
        ('mobile_pc', 'Mobile & PC'),
        ('jobs', 'Job Updates'),
        ('crypto', 'Crypto'),
        ('ai', 'Artificial Intelligence'),
        ('medical_news', 'Medical News'),
        ('ai_medical_imaging', 'AI in Medical Imaging'),
    ]

    name = models.CharField(max_length=200)
    url = models.URLField(max_length=2000, unique=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_active = models.BooleanField(default=True)
    last_fetched = models.DateTimeField(null=True, blank=True)
    fetch_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'RSS Feed'
        verbose_name_plural = 'RSS Feeds'
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class UserBookmark(models.Model):
    """Reading list/bookmarks feature for saving articles"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.CharField(max_length=50)  # 'general', 'python', 'medical_imaging', etc.
    content_id = models.PositiveIntegerField()
    title = models.CharField(max_length=255, blank=True)  # Cache title for display
    link = models.URLField(max_length=2000, blank=True)  # Cache link for quick access
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ['user', 'content_type', 'content_id']
        ordering = ['-created_at']
        verbose_name = 'Bookmark'
        verbose_name_plural = 'Bookmarks'

    def __str__(self):
        return f"{self.user.username}: {self.title[:50]}"


# Create your models here.
class BaseModel(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    pub_date = models.DateTimeField()
    link = models.URLField(max_length=2000)
    content_name = models.CharField(max_length=100)
    guid = models.CharField(max_length=1000)
    image = models.URLField(null=True, max_length=2000)
    source_feed = models.ForeignKey(
        RSSFeed, on_delete=models.SET_NULL, null=True, blank=True, related_name='+'
    )

    class Meta:
        abstract = True
        ordering = ['-pub_date']

    def __str__(self) -> str:
        return f"{self.content_name}: {self.title}"


class GeneralContent(BaseModel):
    pass


class PythonContent(BaseModel):
    pass


class SoftwareDevelopmentContent(BaseModel):
    pass


class CyberSecurityContent(BaseModel):
    pass


class UiUxContent(BaseModel):
    pass


class MobilePcContent(BaseModel):
    pass


class JobUpdatesContent(BaseModel):
    pass

class CryptoContent(BaseModel):
    pass


class AIContent(BaseModel):
    pass


class MedicalNewsContent(BaseModel):
    pass


class AIMedicalImagingContent(BaseModel):
    pass
