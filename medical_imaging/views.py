from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import FormMixin, DeleteView, UpdateView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import MedicalImagingContent, MedicalImagingArticle, ArticleComment
from .forms import MedicalImagingArticleForm, ArticleCommentForm
from blog.models import MedicalNewsContent, AIMedicalImagingContent


class AuthorRequiredMixin:
    """Mixin to check if user can write medical imaging articles"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user-creation:login')
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'profile'):
            if request.user.profile.can_write_to_section('medical_imaging'):
                return super().dispatch(request, *args, **kwargs)
        return redirect('medical_imaging:index')


class MedicalImagingIndexView(ListView):
    """Main landing page for AI & Medical section"""
    template_name = 'medical_imaging/index.html'
    context_object_name = 'rss_contents'
    paginate_by = 12

    def get_queryset(self):
        # Combine both medical news and AI imaging content
        from itertools import chain
        medical = list(MedicalNewsContent.objects.order_by('-pub_date')[:6])
        ai_imaging = list(AIMedicalImagingContent.objects.order_by('-pub_date')[:6])
        combined = sorted(chain(medical, ai_imaging), key=lambda x: x.pub_date, reverse=True)
        return combined[:12]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_article'] = MedicalImagingArticle.objects.filter(
            status='published', is_featured=True
        ).first()
        context['recent_articles'] = MedicalImagingArticle.objects.filter(
            status='published'
        ).order_by('-published_at')[:5]
        return context


class MedicalNewsView(ListView):
    """Medical news and healthcare advancements"""
    template_name = 'medical_imaging/medical_news.html'
    context_object_name = 'contents'
    paginate_by = 20

    def get_queryset(self):
        return MedicalNewsContent.objects.order_by('-pub_date')


class AIImagingNewsView(ListView):
    """AI in Medical Imaging news"""
    template_name = 'medical_imaging/ai_imaging_news.html'
    context_object_name = 'contents'
    paginate_by = 20

    def get_queryset(self):
        return AIMedicalImagingContent.objects.order_by('-pub_date')


class MedicalImagingArticlesView(ListView):
    """List all published user-written articles"""
    model = MedicalImagingArticle
    template_name = 'medical_imaging/articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        queryset = MedicalImagingArticle.objects.filter(status='published')
        topic = self.request.GET.get('topic')
        if topic:
            queryset = queryset.filter(primary_topic=topic)
        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['topics'] = MedicalImagingArticle.TOPIC_CHOICES
        context['current_topic'] = self.request.GET.get('topic', '')
        return context


@method_decorator(csrf_protect, name='dispatch')
class ArticleDetailView(DetailView, FormMixin):
    """Single article view with comments"""
    model = MedicalImagingArticle
    template_name = 'medical_imaging/article_detail.html'
    context_object_name = 'article'
    form_class = ArticleCommentForm
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Allow draft viewing for authors
        if self.request.user.is_authenticated and (
            self.request.user.is_staff or
            (hasattr(self.request.user, 'profile') and
             self.request.user.profile.can_write_to_section('medical_imaging'))
        ):
            return MedicalImagingArticle.objects.all()
        return MedicalImagingArticle.objects.filter(status='published')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['form'] = self.get_form()
        context['related_articles'] = MedicalImagingArticle.objects.filter(
            status='published',
            primary_topic=self.object.primary_topic
        ).exclude(pk=self.object.pk)[:3]
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user-creation:login')
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.article = self.object
        comment.author = self.request.user
        comment.save()
        return redirect(self.object.get_absolute_url())


@method_decorator(csrf_protect, name='dispatch')
class CreateArticleView(AuthorRequiredMixin, View):
    """Create a new medical imaging article"""

    def get(self, request):
        form = MedicalImagingArticleForm()
        return render(request, 'medical_imaging/article_form.html', {
            'form': form,
            'title': 'Write New Article'
        })

    def post(self, request):
        form = MedicalImagingArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            return redirect('medical_imaging:my_articles')
        return render(request, 'medical_imaging/article_form.html', {
            'form': form,
            'title': 'Write New Article'
        })


@method_decorator(csrf_protect, name='dispatch')
class UpdateArticleView(AuthorRequiredMixin, View):
    """Edit an existing article"""

    def get(self, request, slug):
        article = get_object_or_404(MedicalImagingArticle, slug=slug)
        # Only allow author or admin to edit
        if article.author != request.user and not request.user.is_superuser:
            return redirect('medical_imaging:article_detail', slug=slug)
        form = MedicalImagingArticleForm(instance=article)
        return render(request, 'medical_imaging/article_form.html', {
            'form': form,
            'article': article,
            'title': 'Edit Article'
        })

    def post(self, request, slug):
        article = get_object_or_404(MedicalImagingArticle, slug=slug)
        if article.author != request.user and not request.user.is_superuser:
            return redirect('medical_imaging:article_detail', slug=slug)
        form = MedicalImagingArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            return redirect('medical_imaging:article_detail', slug=article.slug)
        return render(request, 'medical_imaging/article_form.html', {
            'form': form,
            'article': article,
            'title': 'Edit Article'
        })


class DeleteArticleView(AuthorRequiredMixin, DeleteView):
    """Delete an article"""
    model = MedicalImagingArticle
    success_url = reverse_lazy('medical_imaging:my_articles')
    template_name = 'medical_imaging/article_confirm_delete.html'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return MedicalImagingArticle.objects.all()
        return MedicalImagingArticle.objects.filter(author=self.request.user)


class PublishArticleView(AuthorRequiredMixin, View):
    """Publish a draft article"""

    def post(self, request, slug):
        article = get_object_or_404(MedicalImagingArticle, slug=slug)
        if article.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        article.status = 'published'
        article.published_at = timezone.now()
        article.save()
        return redirect('medical_imaging:article_detail', slug=article.slug)


class MyArticlesView(AuthorRequiredMixin, ListView):
    """List user's own articles (drafts and published)"""
    model = MedicalImagingArticle
    template_name = 'medical_imaging/my_articles.html'
    context_object_name = 'articles'
    paginate_by = 10

    def get_queryset(self):
        return MedicalImagingArticle.objects.filter(
            author=self.request.user
        ).order_by('-created_at')
