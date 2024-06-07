# Generated by Django 4.2.7 on 2024-06-05 16:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ParametrosRpbf",
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
                ("fondo", models.CharField(db_column="fondo", max_length=3)),
                ("novedad", models.CharField(db_column="novedad", max_length=3)),
                ("bepjtit", models.CharField(db_column="bepjtit", max_length=3)),
                ("bepjben", models.CharField(db_column="bepjben", max_length=3)),
                ("bepjcon", models.CharField(db_column="bepjcon", max_length=3)),
                ("bepjrl", models.CharField(db_column="bepjrl", max_length=3)),
                ("bespjfcp", models.CharField(db_column="bespjfcp", max_length=3)),
                ("bespjf", models.CharField(db_column="bespjf", max_length=3)),
                ("bespjcf", models.CharField(db_column="bespjcf", max_length=3)),
                ("bespjfb", models.CharField(db_column="bespjfb", max_length=3)),
                ("bespjcfe", models.CharField(db_column="bespjcfe", max_length=3)),
                ("becespj", models.CharField(db_column="becespj", max_length=3)),
                ("pppjepj", models.CharField(db_column="pppjepj", max_length=3)),
                ("pbpjepj", models.CharField(db_column="pbpjepj", max_length=3)),
            ],
            options={
                "db_table": "params_reporte_rpbf",
            },
        ),
    ]
