# Generated by Django 4.2.7 on 2024-01-12 17:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fidecomisos', '0002_remove_encargo_numeroproducto_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tipodepersona',
            old_name='description',
            new_name='Description',
        ),
        migrations.RenameField(
            model_name='tipodepersona',
            old_name='id',
            new_name='Id',
        ),
        migrations.RenameField(
            model_name='tipodepersona',
            old_name='tipoPersona',
            new_name='TipoPersona',
        ),
    ]