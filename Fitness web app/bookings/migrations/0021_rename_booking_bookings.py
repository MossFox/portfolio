# Generated by Django 5.1.1 on 2024-12-04 14:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0020_alter_fit_class_teacher_alter_booking_booked_in_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Booking",
            new_name="Bookings",
        ),
    ]
