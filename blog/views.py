from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from datetime import timedelta

from .models import *


@method_decorator(csrf_protect, name='dispatch')
class HomePageView(ListView):
    template_name = "index.html"
    model = GeneralContent
    paginate_by = 20
    context_object_name = 'contents'

    def get_queryset(self):
        return self.model.objects.exclude(image=None).order_by("-pub_date")


@method_decorator(csrf_protect, name='dispatch')
class JobUpdatesPageView(HomePageView):
    template_name = "jobupdatespage.html"
    model = JobUpdatesContent


@method_decorator(csrf_protect, name='dispatch')
class PythonPageView(HomePageView):
    template_name = "pythonpage.html"
    model = PythonContent


@method_decorator(csrf_protect, name='dispatch')
class CyberSecurityPageView(HomePageView):
    template_name = "cybersecuritypage.html"
    model = CyberSecurityContent


@method_decorator(csrf_protect, name='dispatch')
class SoftwareDevelopmentPageView(HomePageView):
    template_name = "softwaredevelopmentpage.html"
    model = SoftwareDevelopmentContent


@method_decorator(csrf_protect, name='dispatch')
class UiUxPageView(HomePageView):
    template_name = "ui_uxpage.html"
    model = UiUxContent


@method_decorator(csrf_protect, name='dispatch')
class MobilePcPageView(HomePageView):
    template_name = "mobile-pcpage.html"
    model = MobilePcContent


@method_decorator(csrf_protect, name='dispatch')
class CryptoPageView(HomePageView):
    template_name = "cryptopage.html"
    model = CryptoContent


@method_decorator(csrf_protect, name='dispatch')
class AIPageView(HomePageView):
    template_name = "aipage.html"
    model = AIContent


class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin to require staff access"""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


@method_decorator(csrf_protect, name='dispatch')
class AdminDashboardView(LoginRequiredMixin, StaffRequiredMixin, TemplateView):
    """Custom admin dashboard with stats, recent activity, and management tools"""
    template_name = "admin_dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        # Content stats
        context['stats'] = {
            'total_general': GeneralContent.objects.count(),
            'total_ai': AIContent.objects.count(),
            'total_crypto': CryptoContent.objects.count(),
            'total_cyber': CyberSecurityContent.objects.count(),
            'total_python': PythonContent.objects.count(),
            'total_software': SoftwareDevelopmentContent.objects.count(),
            'total_uiux': UiUxContent.objects.count(),
            'total_mobile': MobilePcContent.objects.count(),
            'total_jobs': JobUpdatesContent.objects.count(),
            'total_medical': MedicalNewsContent.objects.count(),
            'total_ai_imaging': AIMedicalImagingContent.objects.count(),
        }

        # Calculate total RSS content
        context['total_rss_content'] = sum(context['stats'].values())

        # RSS Feeds
        context['rss_feeds'] = RSSFeed.objects.all().order_by('category', 'name')
        context['active_feeds'] = RSSFeed.objects.filter(is_active=True).count()
        context['inactive_feeds'] = RSSFeed.objects.filter(is_active=False).count()

        # User stats
        context['total_users'] = User.objects.count()
        context['staff_users'] = User.objects.filter(is_staff=True).count()
        context['recent_users'] = User.objects.filter(date_joined__gte=week_ago).count()

        # Recent content (last 10 from each major category)
        context['recent_general'] = GeneralContent.objects.order_by('-pub_date')[:5]
        context['recent_ai'] = AIContent.objects.order_by('-pub_date')[:5]
        context['recent_medical'] = MedicalNewsContent.objects.order_by('-pub_date')[:5]

        # Bookmarks stats
        context['total_bookmarks'] = UserBookmark.objects.count()
        context['recent_bookmarks'] = UserBookmark.objects.filter(created_at__gte=week_ago).count()

        # Import models from other apps for comprehensive stats
        try:
            from forum.models import ForumPost
            context['total_forum_posts'] = ForumPost.objects.count()
            context['recent_forum_posts'] = ForumPost.objects.order_by('-created_at')[:5]
        except:
            context['total_forum_posts'] = 0
            context['recent_forum_posts'] = []

        try:
            from medical_imaging.models import MedicalImagingArticle, ArticleComment
            context['total_medical_articles'] = MedicalImagingArticle.objects.count()
            context['published_medical_articles'] = MedicalImagingArticle.objects.filter(status='published').count()
            context['draft_medical_articles'] = MedicalImagingArticle.objects.filter(status='draft').count()
            context['pending_comments'] = ArticleComment.objects.filter(is_approved=False).count()
            context['recent_medical_articles'] = MedicalImagingArticle.objects.order_by('-created_at')[:5]
        except:
            context['total_medical_articles'] = 0
            context['published_medical_articles'] = 0
            context['draft_medical_articles'] = 0
            context['pending_comments'] = 0
            context['recent_medical_articles'] = []

        try:
            from personal_blog.models import BlogPost
            context['total_blog_posts'] = BlogPost.objects.count()
            context['recent_blog_posts'] = BlogPost.objects.order_by('-created_at')[:5]
        except:
            context['total_blog_posts'] = 0
            context['recent_blog_posts'] = []

        try:
            from stories.models import Story
            context['total_stories'] = Story.objects.count()
            context['recent_stories'] = Story.objects.order_by('-created_at')[:5]
        except:
            context['total_stories'] = 0
            context['recent_stories'] = []

        return context
