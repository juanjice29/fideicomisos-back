# Generated by Django 4.2.7 on 2023-12-07 20:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fidecomisos', '0002_alter_tipodedocumento_descripcion_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='fideicomiso',
            name='Estado',
            field=models.CharField(default='A', max_length=1),
            preserve_default=False,
        ),
    ]
