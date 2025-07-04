# Generated by Django 5.1.1 on 2024-12-03 23:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0018_delete_booking"),
    ]

    operations = [
        migrations.AlterField(
            model_name="fit_class",
            name="teacher",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="Teacher",
                to="bookings.user",
            ),
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "booked_in",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="User_is_booked",
                        to="bookings.user",
                    ),
                ),
                (
                    "class_name",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="Class",
                        to="bookings.timetable",
                    ),
                ),
            ],
        ),
    ]
