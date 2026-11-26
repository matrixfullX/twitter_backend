from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0002_user_auth_provider"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="is_verified_email",
        ),
    ]
