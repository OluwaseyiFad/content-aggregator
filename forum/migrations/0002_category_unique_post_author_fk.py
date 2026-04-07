# Generated manually 2026-04-06
# 1. Adds unique constraint to Category.name (V-2)
# 2. Converts Post.author from a free-text CharField to a proper ForeignKey to User (S-3)
#
# Data migration: existing author strings are matched to User.username. Posts whose
# author username is not found in the database are left with author=NULL (the field
# is nullable so that old data is not silently deleted).

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def populate_author_fk(apps, schema_editor):
    Post = apps.get_model('forum', 'Post')
    User = apps.get_model('auth', 'User')
    for post in Post.objects.exclude(author_legacy__isnull=True).exclude(author_legacy=''):
        user = User.objects.filter(username=post.author_legacy).first()
        if user:
            post.author = user
            post.save(update_fields=['author'])


def reverse_populate_author_fk(apps, schema_editor):
    Post = apps.get_model('forum', 'Post')
    for post in Post.objects.select_related('author'):
        if post.author:
            post.author_legacy = post.author.username
            post.save(update_fields=['author_legacy'])


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Step 1: make Category.name unique
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),

        # Step 2: rename old author CharField so we keep the data during migration
        migrations.RenameField(
            model_name='post',
            old_name='author',
            new_name='author_legacy',
        ),

        # Step 3: add the new FK column (nullable — old posts without a matching user stay NULL)
        migrations.AddField(
            model_name='post',
            name='author',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='forum_posts',
                to=settings.AUTH_USER_MODEL,
            ),
        ),

        # Step 4: populate the FK from legacy username strings
        migrations.RunPython(populate_author_fk, reverse_code=reverse_populate_author_fk),

        # Step 5: drop the legacy column
        migrations.RemoveField(
            model_name='post',
            name='author_legacy',
        ),
    ]
