# Generated by Django 4.2.7 on 2023-12-15 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('actores_de_contrato_cargue', '0003_rename_nombre_actordecontrato_primer_nombre_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='actordecontrato',
            name='Activo',
            field=models.BooleanField(default=True),
        ),
    ]