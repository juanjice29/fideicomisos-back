# Generated by Django 4.2.7 on 2024-07-17 14:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("actores", "0003_remove_relacionfideicomisofuturocomprador_tipoactor"),
    ]

    operations = [
        migrations.AlterModelTable(
            name="futurocomprador",
            table="fidei_futuro_comprador",
        ),
    ]
