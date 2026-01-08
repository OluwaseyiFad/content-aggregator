from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse


class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    body = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    featured_image = models.ImageField(upload_to='personal_blog/featured/', blank=True, null=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            while BlogPost.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('personal_blog:post_detail', kwargs={'slug': self.slug})


class ImageGallery(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='galleries')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Image Gallery'
        verbose_name_plural = 'Image Galleries'

    def __str__(self):
        return f"{self.title} - {self.post.title}"


class GalleryImage(models.Model):
    gallery = models.ForeignKey(ImageGallery, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='personal_blog/gallery/')
    caption = models.CharField(max_length=255, blank=True)
    alt_text = models.CharField(max_length=255, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Gallery Image'
        verbose_name_plural = 'Gallery Images'

    def __str__(self):
        return f"Image {self.order} in {self.gallery.title}"


class ProgressBoard(models.Model):
    post = models.ForeignKey(
        BlogPost, on_delete=models.CASCADE,
        related_name='progress_boards', null=True, blank=True
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress_boards')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Progress Board'
        verbose_name_plural = 'Progress Boards'
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('personal_blog:board_detail', kwargs={'pk': self.pk})


class ProgressColumn(models.Model):
    board = models.ForeignKey(ProgressBoard, on_delete=models.CASCADE, related_name='columns')
    title = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=7, default='#3498db')

    class Meta:
        ordering = ['order']
        verbose_name = 'Progress Column'
        verbose_name_plural = 'Progress Columns'

    def __str__(self):
        return f"{self.title} ({self.board.title})"


class ProgressCard(models.Model):
    column = models.ForeignKey(ProgressColumn, on_delete=models.CASCADE, related_name='cards')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    completed = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Progress Card'
        verbose_name_plural = 'Progress Cards'

    def __str__(self):
        return self.title


class CodeSnippet(models.Model):
    LANGUAGE_CHOICES = [
        ('python', 'Python'),
        ('javascript', 'JavaScript'),
        ('typescript', 'TypeScript'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('sql', 'SQL'),
        ('bash', 'Bash'),
        ('json', 'JSON'),
        ('yaml', 'YAML'),
        ('java', 'Java'),
        ('csharp', 'C#'),
        ('cpp', 'C++'),
        ('go', 'Go'),
        ('rust', 'Rust'),
        ('r', 'R'),
        ('other', 'Other'),
    ]

    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='code_snippets')
    title = models.CharField(max_length=200, blank=True)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES, default='python')
    code = models.TextField()
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = 'Code Snippet'
        verbose_name_plural = 'Code Snippets'

    def __str__(self):
        return self.title or f"Code snippet in {self.post.title}"


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title[:30]}"
