from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponseForbidden
from django.views.generic import View, DetailView, ListView
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from .models import Post, Category, Comments
from .forms import PostForm, CommentsForm


class StaffRequiredMixin(UserPassesTestMixin):
    """Require staff or superuser access; returns 403 on failure."""
    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser


class MyPostView(StaffRequiredMixin, LoginRequiredMixin, ListView):
    model = Post
    template_name = "my_forum_posts.html"
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-created_on').select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


@method_decorator(csrf_protect, name='dispatch')
class CreatePostView(StaffRequiredMixin, LoginRequiredMixin, View):
    def get(self, request):
        form = PostForm()
        return render(request, 'create_post.html', {'form': form})

    def post(self, request):
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('forum:index')
        else:
            return render(request, 'create_post.html', {'form': form})


@method_decorator(csrf_protect, name='dispatch')
class UpdatePostView(StaffRequiredMixin, LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_superuser:
            return HttpResponseForbidden()
        form = PostForm(instance=post)
        return render(request, 'update_post.html', {'form': form})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        if post.author != request.user and not request.user.is_superuser:
            return HttpResponseForbidden()
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('forum:post', pk=pk)
        else:
            return render(request, 'update_post.html', {'form': form})


class DeletePostView(StaffRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy('forum:my-posts')
    template_name = "delete_post.html"


class ForumIndexView(ListView):
    model = Post
    template_name = 'forum_index.html'
    context_object_name = 'posts'
    paginate_by = 10
    ordering = ['-created_on']


class ForumCategoryView(ListView):
    model = Post
    template_name = 'forum_category.html'
    context_object_name = 'posts'
    ordering = ['-created_on']
    paginate_by = 10

    def get_queryset(self):
        category = self.kwargs['category']
        return Post.objects.filter(categories__name__exact=category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.kwargs['category']
        return context


@method_decorator(csrf_protect, name='dispatch')
class ForumPostView(DetailView):
    model = Post
    template_name = 'forum_post.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments_set.order_by('created_on')
        context['comment_form'] = CommentsForm()
        return context

    def post(self, request, pk):
        if not request.user.is_authenticated:
            return redirect('user-creation:login')
        post = get_object_or_404(Post, pk=pk)
        form = CommentsForm(request.POST)
        if form.is_valid():
            Comments.objects.create(
                author=str(request.user),
                body=form.cleaned_data['body'],
                post=post,
            )
            return redirect('forum:post', pk=pk)
        context = self.get_context_data(object=post)
        context['comment_form'] = form
        return render(request, self.template_name, context)
