# Generated by Django 5.1.4 on 2024-12-28 21:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0051_placeholder_user2_placeholder_user3"),
    ]

    operations = [
        migrations.AddField(
            model_name="placeholder",
            name="all",
            field=models.BooleanField(default=False),
        ),
    ]
