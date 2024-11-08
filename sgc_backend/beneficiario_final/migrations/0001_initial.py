# Generated by Django 4.2.7 on 2024-06-11 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("public", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ConsecutivosRpbf",
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
                ("fondo", models.CharField(max_length=3)),
                ("consecutivo", models.IntegerField(db_column="consecutivo")),
            ],
            options={
                "db_table": "rpbf_consecutivos",
            },
        ),
        migrations.CreateModel(
            name="File",
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
                ("file_name", models.CharField(max_length=255)),
                ("file_hash", models.CharField(max_length=32)),
                ("date_inserted", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RpbfHistorico",
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
                ("periodo", models.CharField(max_length=6)),
                ("fondo", models.CharField(max_length=2)),
                ("bepjtit", models.CharField(max_length=2)),
                ("bepjben", models.CharField(max_length=2)),
                ("bepjcon", models.CharField(max_length=2)),
                ("bepjrl", models.CharField(max_length=2)),
                ("bespjfcp", models.CharField(max_length=2)),
                ("bespjf", models.CharField(max_length=2)),
                ("bespjcf", models.CharField(max_length=2)),
                ("bespjfb", models.CharField(max_length=2)),
                ("bespjcfe", models.CharField(max_length=2)),
                ("tdocben", models.CharField(max_length=2)),
                ("niben", models.CharField(max_length=20)),
                ("paexben", models.CharField(max_length=4)),
                ("nitben", models.CharField(max_length=20)),
                ("paexnitben", models.CharField(max_length=4)),
                ("pape", models.CharField(max_length=60)),
                ("sape", models.CharField(max_length=60)),
                ("pnom", models.CharField(max_length=60)),
                ("onom", models.CharField(max_length=60)),
                ("fecnac", models.CharField(max_length=10)),
                ("panacb", models.CharField(max_length=4)),
                ("pnacion", models.CharField(max_length=4)),
                ("paresb", models.CharField(max_length=4)),
                ("dptoben", models.CharField(max_length=2)),
                ("munben", models.CharField(max_length=3)),
                ("dirben", models.CharField(max_length=250)),
                ("codpoben", models.CharField(max_length=10)),
                ("emailben", models.CharField(max_length=50)),
                ("pppjepj", models.CharField(max_length=8)),
                ("pbpjepj", models.CharField(max_length=8)),
                ("feiniben", models.CharField(max_length=10)),
                ("fecfinben", models.CharField(max_length=10)),
                ("tnov", models.CharField(max_length=1)),
                (
                    "tipoNovedad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="public.tiponovedadrpbf",
                    ),
                ),
            ],
            options={
                "db_table": "rpbf_historico",
            },
        ),
        migrations.CreateModel(
            name="RpbfCandidatos",
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
                ("nroIdentif", models.CharField(max_length=20)),
                ("fondo", models.CharField(max_length=2)),
                ("fechaCreacion", models.CharField(max_length=10)),
                ("fechaCancelacion", models.CharField(max_length=10, null=True)),
                ("porcentaje", models.CharField(max_length=7)),
                (
                    "tipoNovedad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="public.tiponovedadrpbf",
                    ),
                ),
            ],
            options={
                "db_table": "rpbf_candidatos",
            },
        ),
        migrations.CreateModel(
            name="Beneficiario_Reporte_Dian",
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
                ("Id_Cliente", models.CharField(max_length=255)),
                ("Periodo", models.CharField(max_length=255)),
                ("Tipo_Producto", models.CharField(max_length=255)),
                (
                    "Tipo_Novedad",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="public.tiponovedadrpbf",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="beneficiario_reporte_dian",
            constraint=models.UniqueConstraint(
                fields=("Id_Cliente", "Tipo_Novedad", "Tipo_Producto"),
                name="unique_identificacion_beneficiario",
            ),
        ),
    ]
