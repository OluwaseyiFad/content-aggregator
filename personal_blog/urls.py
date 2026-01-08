from django.urls import path

from .views import (
    BlogIndexView,
    PostDetailView,
    CreatePostView,
    UpdatePostView,
    DeletePostView,
    PublishPostView,
    MyPostsView,
    ProgressBoardListView,
    ProgressBoardDetailView,
    CreateBoardView,
    MyBoardsView,
    AddCardView,
    MoveCardView,
    ToggleCardView,
)

app_name = 'personal_blog'

urlpatterns = [
    # Blog posts
    path('', BlogIndexView.as_view(), name='index'),
    path('write/', CreatePostView.as_view(), name='create_post'),
    path('my-posts/', MyPostsView.as_view(), name='my_posts'),
    path('post/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', UpdatePostView.as_view(), name='edit_post'),
    path('post/<slug:slug>/delete/', DeletePostView.as_view(), name='delete_post'),
    path('post/<slug:slug>/publish/', PublishPostView.as_view(), name='publish_post'),

    # Progress boards
    path('progress/', ProgressBoardListView.as_view(), name='progress_boards'),
    path('progress/create/', CreateBoardView.as_view(), name='create_board'),
    path('progress/my-boards/', MyBoardsView.as_view(), name='my_boards'),
    path('progress/board/<int:pk>/', ProgressBoardDetailView.as_view(), name='board_detail'),

    # AJAX endpoints for Kanban
    path('api/column/<int:column_id>/add-card/', AddCardView.as_view(), name='add_card'),
    path('api/card/<int:card_id>/move/', MoveCardView.as_view(), name='move_card'),
    path('api/card/<int:card_id>/toggle/', ToggleCardView.as_view(), name='toggle_card'),
]
