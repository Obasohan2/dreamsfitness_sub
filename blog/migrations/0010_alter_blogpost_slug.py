from django.db import migrations
from django.utils.text import slugify


def fix_empty_slugs(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")

    for post in BlogPost.objects.filter(slug=""):
        base_slug = slugify(post.title)
        slug = base_slug
        counter = 1

        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        post.slug = slug
        post.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0009_remove_comment_email_remove_comment_name_and_more"),
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs),
    ]
