# Generated by Django 5.1.1 on 2024-11-29 13:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0006_alter_user_user_permissions_and_more"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="timetable",
            unique_together={("slot", "day", "club", "name")},
        ),
    ]
