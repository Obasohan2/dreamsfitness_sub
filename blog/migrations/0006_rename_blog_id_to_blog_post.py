from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_alter_blogpost_updated_on"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="blog_id",
            new_name="blog_post",
        ),
    ]
