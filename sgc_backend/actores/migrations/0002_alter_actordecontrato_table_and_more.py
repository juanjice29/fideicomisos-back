# Generated by Django 4.2.7 on 2024-05-01 01:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actores', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='actordecontrato',
            table='fidei_actor',
        ),
        migrations.AlterModelTable(
            name='relacionfideicomisoactor',
            table='fidei_actor_fideicomiso',
        ),
        migrations.AlterModelTable(
            name='tipoactordecontrato',
            table='params_tipo_actor',
        ),
    ]
