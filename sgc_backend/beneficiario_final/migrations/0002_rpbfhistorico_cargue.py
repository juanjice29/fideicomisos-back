# Generated by Django 4.2.7 on 2024-06-14 16:51

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("beneficiario_final", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="rpbfhistorico",
            name="cargue",
            field=models.CharField(
                db_column="cargue_id", default=uuid.uuid4, max_length=36, null=True
            ),
        ),
    ]