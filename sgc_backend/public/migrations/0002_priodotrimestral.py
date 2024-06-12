# Generated by Django 4.2.7 on 2024-06-11 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PriodoTrimestral",
            fields=[
                (
                    "periodo",
                    models.CharField(max_length=7, primary_key=True, serialize=False),
                ),
            ],
            options={
                "db_table": "PARAMS_PERIODO_TRIMESTRAL",
            },
        ),
    ]
