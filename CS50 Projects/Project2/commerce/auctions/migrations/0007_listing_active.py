# Generated by Django 5.1.1 on 2024-10-07 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auctions", "0006_rename_wishlist_watchlist_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]
