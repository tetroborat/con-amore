from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views import View

from .cart import Cart as SessionCart
from main_app.models import *


class MainPageView(View):

    @staticmethod
    def get(request):
        context = {
            'title': 'Con Amore',
            'categories': Category.objects.all(),
            'dict_category_products': {
                category: (
                    Product.objects.filter(category=category) if category.name != 'Пиццы' else Pizza.objects.all()
                )
                for category in Category.objects.all()}
        }
        promos = Promo.objects.all()
        if promos.exists():
            context.update({
                'active_promo': promos[0]
            })
            if promos.count() > 1:
                context.update({
                    'promos': promos[1:]
                })
        if 'cart' in request.session:
            context.update({
                'total_price': SessionCart(request).get_total_price()
            })
        return render(
            request=request,
            template_name='main_page.html',
            context=context
        )


class OrderPageView(View):

    @staticmethod
    def get(request):
        return render(
            request=request,
            template_name='order_page.html',
            context={
                'title': 'Con Amore | Оформление заказа',
                'total_price': SessionCart(request).get_total_price()
            }
        )

    @staticmethod
    def post(request, **kwargs):
        Order(
            customer=request.post['input_name'],
            number_customer=request.post['input_phone_number'],
            address=request.post['input_address'],
            cart=SessionCart(request),
            comment=request.post['input_comment']
        )
        return HttpResponseRedirect('/')


class CartModalView(View):

    @staticmethod
    def get(request):
        cart = SessionCart(request)
        context = {
            'session_cart': cart.get_context_for_view(),
            'total_price': cart.get_total_price()
        }
        return render(request, 'cart_modal.html', context)


def AddProductInCart(request):
    product = Product.objects.get(name=request.GET.get('name', None))
    price = request.GET.get('price', None)
    cart = SessionCart(request)
    cart.add(product, price)
    context = {
        'total_price': cart.get_total_price()
    }
    return JsonResponse(context)


def ClearCart(request):
    SessionCart(request).clear()
    return CartModalView.get(request)


def RemoveProductFromCart(request):
    product = Product.objects.get(name=request.GET.get('name', None))
    price = request.GET.get('price', None)
    cart = SessionCart(request)
    quantity = cart.cart[str(product.id)][str(price)]
    if quantity > 1:
        cart.add(product, price, quantity - 1, True)
    else:
        cart.remove(product, price)
    context = {
        'total_price': cart.get_total_price()
    }
    return JsonResponse(context)


def DeleteProductFromCart(request):
    product = Product.objects.get(name=request.GET.get('name', None))
    price = request.GET.get('price', None)
    cart = SessionCart(request)
    cart.remove(product, price)
    context = {
        'total_price': cart.get_total_price()
    }
    return JsonResponse(context)


class ProductsInCartImagesView(View):

    @staticmethod
    def get(request):
        cart = SessionCart(request)
        context = {
            'session_cart': cart.get_context_for_view()
        }
        return render(request, 'products_in_cart_images.html', context)
