# Generated by Django 4.2.7 on 2024-04-26 01:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Log_Changes', '0003_log_cambios_m2m_jsonvalue'),
    ]

    operations = [
        migrations.AddField(
            model_name='log_cambios_m2m',
            name='Action',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
