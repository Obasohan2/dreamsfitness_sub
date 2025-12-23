from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0005_alter_comment_email_alter_comment_name"),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE TABLE blog_blogpost_likes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                blogpost_id BIGINT NOT NULL REFERENCES blog_blogpost(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES auth_user(id) ON DELETE CASCADE,
                UNIQUE(blogpost_id, user_id)
            );
            """,
            reverse_sql="DROP TABLE blog_blogpost_likes;",
        )
    ]
