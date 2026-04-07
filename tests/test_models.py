from django.test import TestCase

from blog.models import *
from forum.models import *


class GeneralContentTestCase(TestCase):
    model = GeneralContent

    def setUp(self):
        self.model.objects.create(
            title="Test Title",
            description="Test Description",
            pub_date="2022-06-01T12:00:00Z",
            link="http://www.testlink.com",
            content_name="Test Content Name",
            guid="12345"
        )

    def test_content_str(self):
        content = self.model.objects.get(title="Test Title")
        self.assertEqual(str(content), "Test Content Name: Test Title")


class SdContentTestCase(GeneralContentTestCase):
    model = SoftwareDevelopmentContent


class PythonContentTestCase(GeneralContentTestCase):
    model = PythonContent


class CyberSecurityContentTestCase(GeneralContentTestCase):
    model = CyberSecurityContent


class UiUxContentTestCase(GeneralContentTestCase):
    model = UiUxContent


class MobilePcContentTestCase(GeneralContentTestCase):
    model = MobilePcContent


# ----------------------------------TEST CASES FOR FORUM APP MODELS-------------------------------------------------#

class CategoryModelTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Technology")
        Category.objects.create(name="Science")

    def test_category_name(self):
        technology = Category.objects.get(name="Technology")
        science = Category.objects.get(name="Science")
        self.assertEqual(technology.name, "Technology")
        self.assertEqual(science.name, "Science")


class PostModelTestCase(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user1 = User.objects.create_user(username="john_smith", password="pass")
        self.user2 = User.objects.create_user(username="jane_doe", password="pass")
        Category.objects.create(name="Technology")
        post = Post.objects.create(
            author=self.user1,
            title="How to build a website",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))
        post = Post.objects.create(
            author=self.user2,
            title="How to build a mobile app",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))

    def test_post_author(self):
        post1 = Post.objects.get(title="How to build a website")
        post2 = Post.objects.get(title="How to build a mobile app")
        self.assertEqual(post1.author, self.user1)
        self.assertEqual(post2.author, self.user2)

    def test_post_categories(self):
        post1 = Post.objects.get(title="How to build a website")
        post2 = Post.objects.get(title="How to build a mobile app")
        self.assertGreater(post1.categories.filter(name="Technology").count(), 0)
        self.assertTrue(post1.categories.filter(name="Technology").exists())


class CommentsModelTestCase(TestCase):
    def setUp(self):
        Category.objects.create(name="Technology")
        post = Post.objects.create(
            title="How to build a website",
            body="Lorem ipsum dolor sit amet...",
        )
        post.categories.set(Category.objects.filter(name="Technology"))
        Comments.objects.create(
            author="Jane Doe",
            body="Great tutorial!",
            post=post,
        )
        Comments.objects.create(
            author="John Doe",
            body="Thanks for sharing!",
            post=post,
        )

    def test_comments_author(self):
        comment1 = Comments.objects.get(id=1)
        comment2 = Comments.objects.get(id=2)
        self.assertEqual(comment1.author, "Jane Doe")
        self.assertEqual(comment2.author, "John Doe")

    def test_comments_post(self):
        comment1 = Comments.objects.get(id=1)
        comment2 = Comments.objects.get(id=2)
        self.assertEqual(comment1.post.title, "How to build a website")
        self.assertEqual(comment2.post.title, "How to build a website")
