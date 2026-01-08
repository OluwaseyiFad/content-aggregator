from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import FormMixin, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import Story, StoryChapter, StoryComment, StoryLike
from .forms import StoryForm, StoryChapterForm, StoryCommentForm


class StoryAuthorRequiredMixin:
    """Mixin to check if user can write stories"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user-creation:login')
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'profile'):
            if request.user.profile.can_write_to_section('stories'):
                return super().dispatch(request, *args, **kwargs)
        return redirect('stories:index')


class StoryIndexView(ListView):
    """List all published stories"""
    model = Story
    template_name = 'stories/index.html'
    context_object_name = 'stories'
    paginate_by = 12

    def get_queryset(self):
        queryset = Story.objects.filter(is_published=True)
        genre = self.request.GET.get('genre')
        if genre:
            queryset = queryset.filter(genre=genre)
        return queryset.order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['genres'] = Story.GENRE_CHOICES
        context['current_genre'] = self.request.GET.get('genre', '')
        context['featured_stories'] = Story.objects.filter(
            is_published=True, is_featured=True
        )[:3]
        return context


@method_decorator(csrf_protect, name='dispatch')
class StoryDetailView(DetailView, FormMixin):
    """Single story view with clean reading experience"""
    model = Story
    template_name = 'stories/story_detail.html'
    context_object_name = 'story'
    form_class = StoryCommentForm
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            # Authors can see their own drafts
            return Story.objects.filter(is_published=True) | Story.objects.filter(
                author=self.request.user
            )
        return Story.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['form'] = self.get_form()
        context['chapters'] = self.object.chapters.all()
        context['like_count'] = self.object.likes.count()
        context['user_liked'] = (
            self.request.user.is_authenticated and
            self.object.likes.filter(user=self.request.user).exists()
        )
        context['related_stories'] = Story.objects.filter(
            is_published=True,
            genre=self.object.genre
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
        comment.story = self.object
        comment.author = self.request.user
        comment.save()
        return redirect(self.object.get_absolute_url())


@method_decorator(csrf_protect, name='dispatch')
class CreateStoryView(StoryAuthorRequiredMixin, View):
    """Create a new story"""

    def get(self, request):
        form = StoryForm()
        return render(request, 'stories/story_form.html', {
            'form': form,
            'title': 'Write New Story'
        })

    def post(self, request):
        form = StoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save(commit=False)
            story.author = request.user
            story.save()
            return redirect('stories:my_stories')
        return render(request, 'stories/story_form.html', {
            'form': form,
            'title': 'Write New Story'
        })


@method_decorator(csrf_protect, name='dispatch')
class UpdateStoryView(StoryAuthorRequiredMixin, View):
    """Edit an existing story"""

    def get(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        if story.author != request.user and not request.user.is_superuser:
            return redirect('stories:story_detail', slug=slug)
        form = StoryForm(instance=story)
        return render(request, 'stories/story_form.html', {
            'form': form,
            'story': story,
            'title': 'Edit Story'
        })

    def post(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        if story.author != request.user and not request.user.is_superuser:
            return redirect('stories:story_detail', slug=slug)
        form = StoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            return redirect('stories:story_detail', slug=story.slug)
        return render(request, 'stories/story_form.html', {
            'form': form,
            'story': story,
            'title': 'Edit Story'
        })


class DeleteStoryView(StoryAuthorRequiredMixin, DeleteView):
    """Delete a story"""
    model = Story
    success_url = reverse_lazy('stories:my_stories')
    template_name = 'stories/story_confirm_delete.html'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Story.objects.all()
        return Story.objects.filter(author=self.request.user)


class PublishStoryView(StoryAuthorRequiredMixin, View):
    """Publish a draft story"""

    def post(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        if story.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        story.is_published = True
        story.published_at = timezone.now()
        story.save()
        return redirect('stories:story_detail', slug=story.slug)


class MyStoriesView(StoryAuthorRequiredMixin, ListView):
    """List user's own stories"""
    model = Story
    template_name = 'stories/my_stories.html'
    context_object_name = 'stories'
    paginate_by = 10

    def get_queryset(self):
        return Story.objects.filter(author=self.request.user).order_by('-created_at')


class AuthorListView(ListView):
    """List all story authors"""
    template_name = 'stories/authors.html'
    context_object_name = 'authors'

    def get_queryset(self):
        return User.objects.filter(
            stories__is_published=True
        ).annotate(
            story_count=Count('stories')
        ).order_by('-story_count')


class AuthorProfileView(DetailView):
    """View an author's profile and their stories"""
    model = User
    template_name = 'stories/author_profile.html'
    context_object_name = 'author'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stories'] = Story.objects.filter(
            author=self.object, is_published=True
        ).order_by('-published_at')
        context['total_stories'] = context['stories'].count()
        context['total_likes'] = StoryLike.objects.filter(
            story__author=self.object
        ).count()
        if hasattr(self.object, 'profile'):
            context['profile'] = self.object.profile
        return context


# AJAX endpoints
@method_decorator(csrf_protect, name='dispatch')
class LikeStoryView(LoginRequiredMixin, View):
    """Like/unlike a story (AJAX)"""

    def post(self, request, slug):
        story = get_object_or_404(Story, slug=slug)
        like, created = StoryLike.objects.get_or_create(
            story=story,
            user=request.user
        )
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'count': story.likes.count()
        })
