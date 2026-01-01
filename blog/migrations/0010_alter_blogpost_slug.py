from django.db import migrations
from django.utils.text import slugify


def fix_empty_slugs(apps, schema_editor):
    BlogPost = apps.get_model("blog", "BlogPost")

    queryset = BlogPost.objects.filter(slug__isnull=True) | BlogPost.objects.filter(slug="")

    for post in queryset:
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
        ("blog", "0010_alter_blogpost_slug"),
    ]

    operations = [
        migrations.RunPython(fix_empty_slugs),
    ]
