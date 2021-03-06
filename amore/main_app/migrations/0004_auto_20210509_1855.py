# Generated by Django 3.2 on 2021-05-09 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0003_auto_20210428_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Сумма заказа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='time_begin',
            field=models.DateTimeField(verbose_name='Время поступления заказа'),
        ),
    ]
