from django.shortcuts import render
from django.views import View

from main_app.models import *


class MainPageView(View):

    def get(self, request, *args, **kwargs):
        promos = Promo.objects.all()
        return render(
            request=request,
            template_name='main_page.html',
            context={
                'title': 'Con Amore',
                'categories': Category.objects.all(),
                'active_promo': promos[0],
                'promos': promos[1:],
                'dict_category_products': {
                    category: Product.objects.filter(category=category)
                    for category in Category.objects.all()
                }
            }
        )


class CartPageView(View):

    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='cart_page.html',
            context={
                'cart': self.order.cart
            }
        )


class OrderPageView(View):

    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='order_page.html',
            context={
                'cart': self.order.cart
            }
        )


class ProductDetailPageView(View):

    def get(self, request, *args, **kwargs):
        return render(
            request=request,
            template_name='product_detail_page.html',
            context={
                'product': Product.objects.get(slug=kwargs['product_slug']),
            }
        )
