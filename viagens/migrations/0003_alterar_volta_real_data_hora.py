from django.db import migrations, models


def converter_volta_real(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        raise RuntimeError(
            "Esta migration foi preparada para PostgreSQL/Supabase."
        )

    Viagem = apps.get_model("viagens", "Viagem")
    banco = schema_editor.connection.alias

    # Impede perder horários se algum registro não tiver data de volta.
    sem_data = (
        Viagem.objects.using(banco)
        .filter(
            horario_volta_real__isnull=False,
            data_volta__isnull=True,
        )
        .exists()
    )

    if sem_data:
        raise RuntimeError(
            "Há viagens com horário real preenchido e sem data_volta. "
            "Preencha a data dessas viagens antes de continuar."
        )

    tabela = schema_editor.quote_name(Viagem._meta.db_table)
    horario = schema_editor.quote_name(
        Viagem._meta.get_field("horario_volta_real").column
    )
    data = schema_editor.quote_name(
        Viagem._meta.get_field("data_volta").column
    )

    schema_editor.execute(
        f"""
        ALTER TABLE {tabela}
        ALTER COLUMN {horario}
        TYPE timestamp with time zone
        USING (
            ({data} + {horario})
            AT TIME ZONE 'America/Sao_Paulo'
        )
        """
    )


class Migration(migrations.Migration):

    dependencies = [
        ("viagens", "0002_motorista_telefone"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(converter_volta_real),
            ],
            state_operations=[
                migrations.AlterField(
                    model_name="viagem",
                    name="horario_volta_real",
                    field=models.DateTimeField(
                        blank=True,
                        null=True,
                        verbose_name="Volta",
                    ),
                ),
            ],
        ),
    ]