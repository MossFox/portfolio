# Generated by Django 5.1.4 on 2024-12-25 16:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0045_day_date_today"),
    ]

    operations = [
        migrations.AlterField(
            model_name="day",
            name="date_today",
            field=models.DateField(default=datetime.date.today),
        ),
    ]
