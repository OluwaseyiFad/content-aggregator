from django.urls import path

from .views import (
    StoryIndexView,
    StoryDetailView,
    CreateStoryView,
    UpdateStoryView,
    DeleteStoryView,
    PublishStoryView,
    MyStoriesView,
    AuthorListView,
    AuthorProfileView,
    LikeStoryView,
)

app_name = 'stories'

urlpatterns = [
    # Main pages
    path('', StoryIndexView.as_view(), name='index'),
    path('authors/', AuthorListView.as_view(), name='authors'),
    path('author/<str:username>/', AuthorProfileView.as_view(), name='author_profile'),

    # Story CRUD
    path('write/', CreateStoryView.as_view(), name='create_story'),
    path('my-stories/', MyStoriesView.as_view(), name='my_stories'),
    path('story/<slug:slug>/', StoryDetailView.as_view(), name='story_detail'),
    path('story/<slug:slug>/edit/', UpdateStoryView.as_view(), name='edit_story'),
    path('story/<slug:slug>/delete/', DeleteStoryView.as_view(), name='delete_story'),
    path('story/<slug:slug>/publish/', PublishStoryView.as_view(), name='publish_story'),

    # AJAX
    path('story/<slug:slug>/like/', LikeStoryView.as_view(), name='like_story'),
]
