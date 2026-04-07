from django.core import mail
from django.test import TestCase, Client
from django.urls import reverse

from forum.models import Category, Post, Comments


class HomePageViewTestCase(TestCase):
    url = '/'
    template = 'index.html'

    def setUp(self):
        self.client = Client()

    def test_page_view(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, self.template)


class PythonPageViewTestCase(HomePageViewTestCase):
    url = '/python/'
    template = 'pythonpage.html'


class SdPageViewTestCase(HomePageViewTestCase):
    url = '/software-development/'
    template = 'softwaredevelopmentpage.html'


class CyberSecurityPageViewTestCase(HomePageViewTestCase):
    url = '/cyber-security/'
    template = 'cybersecuritypage.html'


class UiUxPageViewTestCase(HomePageViewTestCase):
    url = '/ui-ux/'
    template = 'ui_uxpage.html'


class MobilePcViewTestCase(HomePageViewTestCase):
    url = '/mobile-pc/'
    template = 'mobile-pcpage.html'


# --------------------------------------------TEST CASES FOR FORUM VIEWS-------------------------------------------#

class IndexViewTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Technology")
        Category.objects.create(name="Science")
        post = Post.objects.create(
            title="How to build a website",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))
        post = Post.objects.create(
            title="How to build a mobile app",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))

    def test_index_view(self):
        response = self.client.get(reverse('forum:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technology")
        self.assertContains(response, "How to build a website")
        self.assertContains(response, "How to build a mobile app")


class CategoryViewTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Technology")
        Category.objects.create(name="Science")
        post = Post.objects.create(
            title="How to build a website",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))
        post = Post.objects.create(
            title="How to build a mobile app",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))

    def test_category_view(self):
        response = self.client.get(reverse('forum:category', kwargs={'category': 'Technology'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Technology")
        self.assertContains(response, "How to build a website")
        self.assertContains(response, "How to build a mobile app")


class PostViewTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Technology")
        self.post = Post.objects.create(
            title="How to build a website",
            body="Lorem ipsum dolor sit amet...",
        )
        self.post.categories.set(Category.objects.filter(name="Technology"))
        Comments.objects.create(
            author="Jane Doe",
            body="Great tutorial!",
            post=self.post,
        )
        Comments.objects.create(
            author="John Doe",
            body="Thanks for sharing!",
            post=self.post,
        )

    def test_post_view(self):
        response = self.client.get(reverse('forum:post', kwargs={'pk': self.post.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "How to build a website")
