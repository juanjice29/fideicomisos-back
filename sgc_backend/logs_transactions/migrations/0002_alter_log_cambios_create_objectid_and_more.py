# Generated by Django 5.0.6 on 2024-07-11 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("logs_transactions", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="log_cambios_create",
            name="objectId",
            field=models.CharField(db_column="object_id", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="log_cambios_delete",
            name="objectId",
            field=models.CharField(db_column="object_id", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="log_cambios_m2m",
            name="objectId",
            field=models.CharField(db_column="object_id", max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="log_cambios_update",
            name="objectId",
            field=models.CharField(db_column="object_id", max_length=255, null=True),
        ),
        migrations.AlterUniqueTogether(
            name="log_cambios_create",
            unique_together={("objectId", "tiempoAccion", "nombreModelo")},
        ),
        migrations.AlterUniqueTogether(
            name="log_cambios_delete",
            unique_together={("objectId", "tiempoAccion", "nombreModelo")},
        ),
        migrations.AlterUniqueTogether(
            name="log_cambios_m2m",
            unique_together={("objectId", "tiempoAccion", "nombreModelo")},
        ),
        migrations.AlterUniqueTogether(
            name="log_cambios_update",
            unique_together={("objectId", "tiempoAccion", "nombreModelo")},
        ),
    ]
