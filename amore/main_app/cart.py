import json

from django.conf import settings
from .models import Product
from decimal import Decimal


class Cart(object):

    def __init__(self, request):
        """
        Инициализируем корзину
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, price, quantity=1, update_quantity=False):
        """
        Добавить продукт в корзину или обновить его количество.
        """
        product_id = str(product.id)
        if product_id not in self.cart or price not in self.cart[product_id]:
            if product_id not in self.cart:
                self.cart[product_id] = {price: 0}
            else:
                self.cart[product_id][price] = 0
        if update_quantity:
            self.cart[product_id][price] = quantity
        else:
            self.cart[product_id][price] += quantity
        self.save()

    def save(self):
        # Обновление сессии cart
        self.session[settings.CART_SESSION_ID] = self.cart
        # Отметить сеанс как "измененный", чтобы убедиться, что он сохранен
        self.session.modified = True

    def remove(self, product, price):
        """
        Удаление товара из корзины.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id][price]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        product_ids = self.cart.keys()
        # получение объектов product и добавление их в корзину
        products = Product.objects.filter(id__in=product_ids)

        for id_product, item in self.cart.items():
            for price, quantity in item.items():
                yield {
                    'product': products.get(pk=id_product),
                    'price': int(price),
                    'quantity': quantity,
                    'total_price': int(price) * quantity
                }

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(
            sum(
                Decimal(price) * quantity
                for price, quantity in item.items()
            )
            for item in self.cart.values()
        )

    def clear(self):
        # удаление корзины из сессии
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_context_for_view(self):
        return [
            {
                'product': item['product'],
                'quantity': item['quantity'],
                'price': int(item['price'])
            }
            for item in self
        ]

    def __str__(self):
        return ''.join([
            f"{item['quantity']} x {item['product'].name} ({int(item['price'])} ₽)\n"
            if item['product'].category.name != 'Пиццы' else
            f"{item['quantity']} x {item['product'].name} - {'20см' if item['product'].price == int(item['price']) else '30см'} ({int(item['price'])} ₽)\n"
            for item in self
        ])
