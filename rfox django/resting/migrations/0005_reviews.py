# Generated by Django 5.1.1 on 2025-03-01 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resting', '0004_alter_schedule_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reviews',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review', models.CharField(max_length=1028)),
                ('author', models.CharField(max_length=28)),
            ],
        ),
    ]
