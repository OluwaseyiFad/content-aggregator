from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended user profile for role-based permissions and author features"""

    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('author', 'Author'),
        ('reader', 'Reader'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    display_name = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)

    # Author-specific fields
    is_verified_author = models.BooleanField(default=False)
    author_sections = models.JSONField(default=list, blank=True)  # ['stories', 'medical_imaging', 'personal_blog']

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.role}"

    def can_write_to_section(self, section):
        """Check if user can write to a specific section"""
        if self.user.is_superuser or self.role == 'admin':
            return True
        if self.role == 'author' and section in self.author_sections:
            return True
        return False

    @property
    def get_display_name(self):
        """Return display name or username"""
        return self.display_name or self.user.username


# Auto-create profile when user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
