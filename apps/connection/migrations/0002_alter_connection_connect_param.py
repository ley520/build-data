# Generated by Django 3.2 on 2023-03-09 10:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("connection", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="connection",
            name="connect_param",
            field=models.JSONField(),
        ),
    ]
