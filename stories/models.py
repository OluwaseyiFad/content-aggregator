import re
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class Story(models.Model):
    GENRE_CHOICES = [
        ('fiction', 'Fiction'),
        ('fantasy', 'Fantasy'),
        ('romance', 'Romance'),
        ('mystery', 'Mystery'),
        ('scifi', 'Science Fiction'),
        ('horror', 'Horror'),
        ('drama', 'Drama'),
        ('comedy', 'Comedy'),
        ('adventure', 'Adventure'),
        ('poetry', 'Poetry'),
        ('other', 'Other'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.TextField(max_length=1000)
    body = models.TextField()
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    word_count = models.PositiveIntegerField(default=0, editable=False)
    reading_time = models.PositiveIntegerField(default=0, editable=False)
    cover_image = models.ImageField(upload_to='stories/covers/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while Story.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        words = len(re.findall(r'\w+', self.body))
        self.word_count = words
        self.reading_time = max(1, words // 200)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('stories:story_detail', kwargs={'slug': self.slug})


class StoryChapter(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    body = models.TextField()
    order = models.PositiveIntegerField(default=0)
    word_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['order']
        verbose_name = 'Story Chapter'
        verbose_name_plural = 'Story Chapters'

    def __str__(self):
        return f"Chapter {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        words = len(re.findall(r'\w+', self.body))
        self.word_count = words
        super().save(*args, **kwargs)


class StoryComment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.story.title[:30]}"


class StoryLike(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['story', 'user']

    def __str__(self):
        return f"{self.user.username} likes {self.story.title}"
