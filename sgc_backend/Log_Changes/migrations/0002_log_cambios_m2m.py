# Generated by Django 4.2.7 on 2024-04-26 01:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Log_Changes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log_Cambios_M2M',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Ip', models.GenericIPAddressField()),
                ('TiempoAccion', models.DateTimeField(auto_now_add=True)),
                ('NombreModelo', models.CharField(max_length=50)),
                ('NombreCampo', models.CharField(max_length=50)),
                ('Valor', models.TextField(null=True)),
                ('object_id', models.PositiveIntegerField()),
                ('request_id', models.CharField(default=uuid.uuid4, max_length=36, null=True)),
                ('Usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
            ],
        ),
    ]