# Generated by Django 4.2.7 on 2023-12-28 15:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fidecomisos', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='encargo',
            name='NumeroProducto',
        ),
        migrations.RemoveField(
            model_name='encargotemporal',
            name='NumeroProducto',
        ),
    ]
