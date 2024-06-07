# Generated by Django 4.2.7 on 2024-06-05 14:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="Log_Cambios_Update",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(db_column="ip")),
                (
                    "tiempoAccion",
                    models.DateTimeField(auto_now_add=True, db_column="tiempo_accion"),
                ),
                (
                    "nombreModelo",
                    models.CharField(db_column="nombre_modelo", max_length=50),
                ),
                (
                    "cambiosValor",
                    models.TextField(db_column="cambios_valor", null=True),
                ),
                (
                    "objectId",
                    models.CharField(db_column="object_id", max_length=255, null=True),
                ),
                (
                    "signalId",
                    models.CharField(
                        db_column="signal_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "requestId",
                    models.CharField(
                        db_column="request_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "contentType",
                    models.ForeignKey(
                        db_column="content_type",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="usuario",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "logs_update",
            },
        ),
        migrations.CreateModel(
            name="Log_Cambios_M2M",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(db_column="ip")),
                (
                    "tiempoAccion",
                    models.DateTimeField(auto_now_add=True, db_column="tiempo_accion"),
                ),
                (
                    "nombreModelo",
                    models.CharField(db_column="nombre_modelo", max_length=50),
                ),
                (
                    "objectId",
                    models.CharField(db_column="object_id", max_length=255, null=True),
                ),
                (
                    "nombreModeloPadre",
                    models.CharField(db_column="nombre_modelo_padre", max_length=50),
                ),
                (
                    "objectIdPadre",
                    models.CharField(
                        db_column="object_id_padre", max_length=255, null=True
                    ),
                ),
                ("jsonValue", models.TextField(db_column="json_value", null=True)),
                (
                    "accion",
                    models.CharField(db_column="accion", max_length=50, null=True),
                ),
                (
                    "signalId",
                    models.CharField(
                        db_column="signal_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "requestId",
                    models.CharField(
                        db_column="request_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "contentType",
                    models.ForeignKey(
                        db_column="content_type",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log_cambios_m2m_content",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "contentTypePadre",
                    models.ForeignKey(
                        db_column="content_type_padre",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="log_cambios_m2m_content_padre",
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="usuario",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "logs_relate",
            },
        ),
        migrations.CreateModel(
            name="Log_Cambios_Delete",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(db_column="ip")),
                (
                    "tiempoAccion",
                    models.DateTimeField(auto_now_add=True, db_column="tiempo_accion"),
                ),
                (
                    "nombreModelo",
                    models.CharField(db_column="nombre_modelo", max_length=50),
                ),
                (
                    "antiguoValor",
                    models.TextField(db_column="antiguo_valor", null=True),
                ),
                (
                    "objectId",
                    models.CharField(db_column="object_id", max_length=255, null=True),
                ),
                (
                    "signalId",
                    models.CharField(
                        db_column="signal_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "requestId",
                    models.CharField(
                        db_column="request_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "contentType",
                    models.ForeignKey(
                        db_column="content_type",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="usuario",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "logs_delete",
            },
        ),
        migrations.CreateModel(
            name="Log_Cambios_Create",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("ip", models.GenericIPAddressField(db_column="ip")),
                (
                    "tiempoAccion",
                    models.DateTimeField(auto_now_add=True, db_column="tiempo_accion"),
                ),
                (
                    "nombreModelo",
                    models.CharField(db_column="nombre_modelo", max_length=50),
                ),
                ("nuevoValor", models.TextField(db_column="nuevo_valor", null=True)),
                (
                    "objectId",
                    models.CharField(db_column="object_id", max_length=255, null=True),
                ),
                (
                    "signalId",
                    models.CharField(
                        db_column="signal_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "requestId",
                    models.CharField(
                        db_column="request_id",
                        default=uuid.uuid4,
                        max_length=36,
                        null=True,
                    ),
                ),
                (
                    "contentType",
                    models.ForeignKey(
                        db_column="content_type",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
                (
                    "usuario",
                    models.ForeignKey(
                        db_column="usuario",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "db_table": "logs_create",
            },
        ),
    ]
