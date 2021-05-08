# Generated by Django 3.2 on 2021-05-08 20:13

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_auto_20210411_1539'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pizza',
            fields=[
                ('product_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='main_app.product')),
                ('optional_price', models.PositiveIntegerField(verbose_name='Цена большой пиццы')),
            ],
            bases=('main_app.product',),
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product',
        ),
        migrations.RemoveField(
            model_name='product',
            name='complex_composition',
        ),
        migrations.AddField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=8, verbose_name='Сумма заказа'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='order',
            name='cart',
            field=models.TextField(verbose_name='Корзина'),
        ),
        migrations.AlterField(
            model_name='order',
            name='time_begin',
            field=models.DateTimeField(default=datetime.datetime(2021, 5, 8, 23, 13, 24, 812364), verbose_name='Время поступления заказа'),
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
