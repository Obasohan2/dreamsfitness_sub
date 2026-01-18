from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "000X_previous_migration_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="updated_on",
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
