# Generated by Django 5.1.4 on 2024-12-25 17:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0048_remove_day_date_today_alter_time_timestamp"),
    ]

    operations = [
        migrations.AddField(
            model_name="day",
            name="date_today",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name="time",
            name="timestamp",
            field=models.TimeField(default=models.CharField(max_length=10)),
        ),
    ]
