from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from transliterate import translit
from django.db import models


class Product(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    category = models.ForeignKey(
        verbose_name='Категория',
        to='Category',
        on_delete=models.CASCADE
    )
    time_cooking = models.DurationField(
        verbose_name='Продолжительность готовки'
    )
    availability = models.BooleanField(
        verbose_name='Наличие',
        default=True
    )
    description = models.TextField(
        verbose_name='Состав',
        null=True,
        blank=True
    )
    slug = models.SlugField(
        verbose_name='Кодовое обозначение (заполняется авт-ки)',
        blank=True
    )
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='products'
    )
    price = models.PositiveIntegerField(
        verbose_name='Цена'
    )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        slug = translit(
                self.name.__str__(),
                'ru',
                reversed=True
            )
        self.slug = slugify(slug)
        super(Product, self).save(kwargs)

    def get_url(self):
        return reverse('', kwargs={
            'category_slug': self.category.slug,
            'product_slug': self.slug
        })


class Category(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255
    )
    slug = models.SlugField(
        verbose_name='Кодовое обозначение (заполняется авт-ки)',
        blank=True
    )
    image_icon = models.ImageField(
        verbose_name='Иконка',
        upload_to='icons'
    )

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        slug = translit(
            self.name.__str__(),
            'ru',
            reversed=True
        )
        self.slug = slugify(slug)
        super(Category, self).save(kwargs)

    def get_url(self):
        return reverse('', kwargs={
            'category_slug': self.slug
        })


class Order(models.Model):
    time_begin = models.DateTimeField(
        verbose_name='Время поступления заказа'
    )
    customer = models.CharField(
        verbose_name='Заказчик',
        max_length=200
    )
    number_customer = models.CharField(
        verbose_name='Контактный телефон',
        max_length=12
    )
    address = models.CharField(
        verbose_name='Адрес доставки',
        max_length=255
    )
    cart = models.TextField(
        verbose_name='Корзина'
    )
    total_price = models.DecimalField(
        verbose_name='Сумма заказа',
        decimal_places=2,
        max_digits=8
    )
    comment = models.TextField(
        verbose_name='Комментарий к заказу',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.time_begin.strftime("%d.%m.%Y %H:%M")}  |  {self.customer}  |  {self.number_customer}  |  {self.total_price} ₽'

    def get_url(self):
        return reverse('order_detail', kwargs={
            'order_id': self.pk
        })


class Promo(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=200
    )
    banner = models.ImageField(
        verbose_name='Баннер',
        upload_to='promos'
    )

    def __str__(self):
        return self.name


class Pizza(Product):
    optional_price = models.PositiveIntegerField(
        verbose_name='Цена большой пиццы'
    )