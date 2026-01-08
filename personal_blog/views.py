from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import FormMixin, DeleteView
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import BlogPost, ProgressBoard, ProgressColumn, ProgressCard, ImageGallery, GalleryImage
from .forms import BlogPostForm, ProgressBoardForm, ProgressColumnForm, ProgressCardForm, BlogCommentForm


class AuthorRequiredMixin:
    """Mixin to check if user can write personal blog posts"""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('user-creation:login')
        if request.user.is_superuser or request.user.is_staff:
            return super().dispatch(request, *args, **kwargs)
        if hasattr(request.user, 'profile'):
            if request.user.profile.can_write_to_section('personal_blog'):
                return super().dispatch(request, *args, **kwargs)
        return redirect('personal_blog:index')


class BlogIndexView(ListView):
    """List all published blog posts"""
    model = BlogPost
    template_name = 'personal_blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True).order_by('-published_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = BlogPost.objects.filter(
            is_published=True, is_featured=True
        )[:3]
        return context


@method_decorator(csrf_protect, name='dispatch')
class PostDetailView(DetailView, FormMixin):
    """Single blog post view with comments"""
    model = BlogPost
    template_name = 'personal_blog/post_detail.html'
    context_object_name = 'post'
    form_class = BlogCommentForm
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_staff:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.filter(is_approved=True)
        context['form'] = self.get_form()
        context['galleries'] = self.object.galleries.all()
        context['code_snippets'] = self.object.code_snippets.all()
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
        comment.post = self.object
        comment.author = self.request.user
        comment.save()
        return redirect(self.object.get_absolute_url())


@method_decorator(csrf_protect, name='dispatch')
class CreatePostView(AuthorRequiredMixin, View):
    """Create a new blog post"""

    def get(self, request):
        form = BlogPostForm()
        return render(request, 'personal_blog/post_form.html', {
            'form': form,
            'title': 'Write New Post'
        })

    def post(self, request):
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('personal_blog:my_posts')
        return render(request, 'personal_blog/post_form.html', {
            'form': form,
            'title': 'Write New Post'
        })


@method_decorator(csrf_protect, name='dispatch')
class UpdatePostView(AuthorRequiredMixin, View):
    """Edit an existing post"""

    def get(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        if post.author != request.user and not request.user.is_superuser:
            return redirect('personal_blog:post_detail', slug=slug)
        form = BlogPostForm(instance=post)
        return render(request, 'personal_blog/post_form.html', {
            'form': form,
            'post': post,
            'title': 'Edit Post'
        })

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        if post.author != request.user and not request.user.is_superuser:
            return redirect('personal_blog:post_detail', slug=slug)
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('personal_blog:post_detail', slug=post.slug)
        return render(request, 'personal_blog/post_form.html', {
            'form': form,
            'post': post,
            'title': 'Edit Post'
        })


class DeletePostView(AuthorRequiredMixin, DeleteView):
    """Delete a post"""
    model = BlogPost
    success_url = reverse_lazy('personal_blog:my_posts')
    template_name = 'personal_blog/post_confirm_delete.html'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return BlogPost.objects.all()
        return BlogPost.objects.filter(author=self.request.user)


class PublishPostView(AuthorRequiredMixin, View):
    """Publish a draft post"""

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug)
        if post.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        post.is_published = True
        post.published_at = timezone.now()
        post.save()
        return redirect('personal_blog:post_detail', slug=post.slug)


class MyPostsView(AuthorRequiredMixin, ListView):
    """List user's own posts"""
    model = BlogPost
    template_name = 'personal_blog/my_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user).order_by('-created_at')


# Progress Board Views
class ProgressBoardListView(ListView):
    """List all public progress boards"""
    model = ProgressBoard
    template_name = 'personal_blog/progress_boards.html'
    context_object_name = 'boards'
    paginate_by = 10

    def get_queryset(self):
        return ProgressBoard.objects.filter(is_public=True).order_by('-updated_at')


class ProgressBoardDetailView(DetailView):
    """View a single progress board (Kanban view)"""
    model = ProgressBoard
    template_name = 'personal_blog/progress_board_detail.html'
    context_object_name = 'board'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return ProgressBoard.objects.filter(
                is_public=True
            ) | ProgressBoard.objects.filter(author=self.request.user)
        return ProgressBoard.objects.filter(is_public=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['columns'] = self.object.columns.prefetch_related('cards').all()
        context['can_edit'] = (
            self.request.user.is_authenticated and
            (self.object.author == self.request.user or self.request.user.is_superuser)
        )
        return context


@method_decorator(csrf_protect, name='dispatch')
class CreateBoardView(AuthorRequiredMixin, View):
    """Create a new progress board"""

    def get(self, request):
        form = ProgressBoardForm()
        return render(request, 'personal_blog/board_form.html', {
            'form': form,
            'title': 'Create Progress Board'
        })

    def post(self, request):
        form = ProgressBoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.author = request.user
            board.save()
            # Create default columns
            ProgressColumn.objects.create(board=board, title='To Do', order=0, color='#e74c3c')
            ProgressColumn.objects.create(board=board, title='In Progress', order=1, color='#f39c12')
            ProgressColumn.objects.create(board=board, title='Done', order=2, color='#27ae60')
            return redirect('personal_blog:board_detail', pk=board.pk)
        return render(request, 'personal_blog/board_form.html', {
            'form': form,
            'title': 'Create Progress Board'
        })


class MyBoardsView(AuthorRequiredMixin, ListView):
    """List user's own boards"""
    model = ProgressBoard
    template_name = 'personal_blog/my_boards.html'
    context_object_name = 'boards'

    def get_queryset(self):
        return ProgressBoard.objects.filter(author=self.request.user).order_by('-updated_at')


# AJAX endpoints for Kanban board
@method_decorator(csrf_protect, name='dispatch')
class AddCardView(AuthorRequiredMixin, View):
    """Add a card to a column (AJAX)"""

    def post(self, request, column_id):
        column = get_object_or_404(ProgressColumn, pk=column_id)
        if column.board.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        title = request.POST.get('title', '').strip()
        if not title:
            return JsonResponse({'error': 'Title required'}, status=400)

        card = ProgressCard.objects.create(
            column=column,
            title=title,
            order=column.cards.count()
        )
        return JsonResponse({
            'id': card.pk,
            'title': card.title,
            'completed': card.completed
        })


@method_decorator(csrf_protect, name='dispatch')
class MoveCardView(AuthorRequiredMixin, View):
    """Move a card to a different column (AJAX)"""

    def post(self, request, card_id):
        card = get_object_or_404(ProgressCard, pk=card_id)
        if card.column.board.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        new_column_id = request.POST.get('column_id')
        new_order = request.POST.get('order', 0)

        if new_column_id:
            new_column = get_object_or_404(ProgressColumn, pk=new_column_id)
            card.column = new_column
        card.order = int(new_order)
        card.save()

        return JsonResponse({'status': 'success'})


@method_decorator(csrf_protect, name='dispatch')
class ToggleCardView(AuthorRequiredMixin, View):
    """Toggle card completion status (AJAX)"""

    def post(self, request, card_id):
        card = get_object_or_404(ProgressCard, pk=card_id)
        if card.column.board.author != request.user and not request.user.is_superuser:
            return JsonResponse({'error': 'Unauthorized'}, status=403)

        card.completed = not card.completed
        card.save()
        return JsonResponse({'completed': card.completed})
