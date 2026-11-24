from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("viagens", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="motorista",
            name="telefone",
            field=models.CharField(
                blank=True,
                default="",
                max_length=20,
                verbose_name="Telefone",
            ),
        ),
    ]