# Generated by Django 4.2.7 on 2024-07-17 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("public", "0003_alter_parametrosgenericos_nombre"),
        (
            "actores",
            "0007_remove_relacionfideicomisofuturocomprador_unique_fideicomiso_futuro_comprador_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="futurocomprador",
            name="tipoPersona",
            field=models.ForeignKey(
                db_column="tipo_persona",
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="public.tipodepersona",
            ),
            preserve_default=False,
        ),
    ]