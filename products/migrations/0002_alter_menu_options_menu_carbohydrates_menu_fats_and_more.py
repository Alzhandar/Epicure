# Generated by Django 5.1.6 on 2025-04-02 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="menu",
            options={"verbose_name": "Меню", "verbose_name_plural": "Меню"},
        ),
        migrations.AddField(
            model_name="menu",
            name="carbohydrates",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Укажите количество углеводов в граммах",
                max_digits=5,
                null=True,
                verbose_name="Углеводы (г)",
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="fats",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Укажите количество жиров в граммах",
                max_digits=5,
                null=True,
                verbose_name="Жиры (г)",
            ),
        ),
        migrations.AddField(
            model_name="menu",
            name="proteins",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text="Укажите количество белков в граммах",
                max_digits=5,
                null=True,
                verbose_name="Белки (г)",
            ),
        ),
    ]
