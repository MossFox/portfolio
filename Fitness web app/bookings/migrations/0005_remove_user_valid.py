# Generated by Django 5.1.1 on 2024-11-25 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0004_alter_user_options_alter_user_managers_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="valid",
        ),
    ]
