# Generated by Django 5.1.1 on 2024-12-03 17:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0012_rename_capacity_fit_class_capacity"),
    ]

    operations = [
        migrations.RenameField(
            model_name="fit_class",
            old_name="CAPACITY",
            new_name="capacity",
        ),
    ]
