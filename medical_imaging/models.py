from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

from blog.models import BaseModel


class MedicalImagingContent(BaseModel):
    class Meta:
        verbose_name = 'Medical Imaging Content'
        verbose_name_plural = 'Medical Imaging Contents'
        ordering = ['-pub_date']


class MedicalImagingArticle(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('review', 'In Review'),
        ('published', 'Published'),
    ]

    TOPIC_CHOICES = [
        ('fairness', 'Fairness & Equity'),
        ('bias', 'Bias Detection'),
        ('ethics', 'Ethics'),
        ('regulation', 'Regulation & Policy'),
        ('clinical', 'Clinical Applications'),
        ('research', 'Research'),
        ('tutorial', 'Tutorial'),
        ('news', 'Industry News'),
    ]

    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='medical_articles'
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.TextField(max_length=500)
    body = models.TextField()
    featured_image = models.ImageField(
        upload_to='medical_imaging/featured/', blank=True, null=True
    )

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    primary_topic = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    is_featured = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Medical Imaging Article'
        verbose_name_plural = 'Medical Imaging Articles'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while MedicalImagingArticle.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('medical_imaging:article_detail', kwargs={'slug': self.slug})

    @property
    def reading_time(self):
        import re
        word_count = len(re.findall(r'\w+', self.body))
        return max(1, word_count // 200)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        MedicalImagingArticle, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='medical_imaging/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Article Image'
        verbose_name_plural = 'Article Images'

    def __str__(self):
        return f"Image for: {self.article.title[:30]}"


class ArticleComment(models.Model):
    article = models.ForeignKey(
        MedicalImagingArticle, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title[:30]}"
