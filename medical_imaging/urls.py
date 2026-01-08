from django.urls import path

from .views import (
    MedicalImagingIndexView,
    MedicalImagingArticlesView,
    ArticleDetailView,
    CreateArticleView,
    UpdateArticleView,
    DeleteArticleView,
    PublishArticleView,
    MyArticlesView,
    MedicalNewsView,
    AIImagingNewsView,
)

app_name = 'medical_imaging'

urlpatterns = [
    # Main pages
    path('', MedicalImagingIndexView.as_view(), name='index'),
    path('medical-news/', MedicalNewsView.as_view(), name='medical_news'),
    path('ai-imaging/', AIImagingNewsView.as_view(), name='ai_imaging'),
    path('articles/', MedicalImagingArticlesView.as_view(), name='articles'),

    # Article CRUD
    path('write/', CreateArticleView.as_view(), name='create_article'),
    path('my-articles/', MyArticlesView.as_view(), name='my_articles'),
    path('article/<slug:slug>/', ArticleDetailView.as_view(), name='article_detail'),
    path('article/<slug:slug>/edit/', UpdateArticleView.as_view(), name='edit_article'),
    path('article/<slug:slug>/delete/', DeleteArticleView.as_view(), name='delete_article'),
    path('article/<slug:slug>/publish/', PublishArticleView.as_view(), name='publish_article'),
]
