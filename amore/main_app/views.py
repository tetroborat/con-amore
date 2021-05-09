from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe

from amore.settings import TOKEN, MY_ID
from .cart import Cart as SessionCart
from django.shortcuts import render
from django.views import View
from main_app.models import *
from .models import Product

from telepot import Bot


telegramBot = Bot(TOKEN)


def send_message(text):
    telegramBot.sendMessage(MY_ID, text, parse_mode="Markdown")


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
        cart = SessionCart(request)
        order = Order(
            time_begin=timezone.datetime.now(),
            customer=request.POST.get('input_name'),
            number_customer=request.POST.get('input_phone_number'),
            address=request.POST.get('input_address') if request.POST.get('check_address') != 'on' else 'Самовывоз',
            cart=cart,
            total_price=cart.get_total_price(),
            comment=request.POST.get('input_comment')
        )
        order.save()
        message = f'*Заказ №{order.pk}*\n\n' \
                  f'{order.cart}\n' \
                  f'*Итого: {order.total_price} ₽*\n\n' \
                  f'{order.customer}\n' \
                  f'{order.address}\n' \
                  f'{order.number_customer}'
        if order.comment != '':
            message += f'\nКомментарий: {order.comment}'
        send_message(message)
        messages.success(request, mark_safe(f'Скоро мы позвоним Вам! Заказ <a href="{order.get_url()}" class="alert-link">номер №{order.pk}</a> поступил в обработку.'))
        cart.clear()
        return HttpResponseRedirect('/')


class CartModalView(View):

    @staticmethod
    def get(request):
        cart = SessionCart(request)
        context = {
            'session_cart': cart.get_context_for_view(),
            'total_price': cart.get_total_price(),
            'check_modal': request.META.get('HTTP_REFERER').split('/')[-2] != 'order'
        }
        return render(request, 'cart_modal.html', context)


def AddProductInCart(request):
    product = Product.objects.get(slug=request.GET.get('slug', None))
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
    product = Product.objects.get(slug=request.GET.get('slug', None))
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
    product = Product.objects.get(slug=request.GET.get('slug', None))
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


class ContactsView(View):

    @staticmethod
    def get(request):
        context = {
            'title': 'Con Amore | Контакты'
        }
        return render(request, 'contacts.html', context)


class AboutUsView(View):

    @staticmethod
    def get(request):
        return render(request, 'about_us.html')


class OrderDetailPageView(View):

    @staticmethod
    def get(request, **kwargs):
        order = Order.objects.get(id=int(kwargs["order_id"]))
        cart = order.cart
        return render(request, 'order_detail_page.html', {
            'title': f'Con Amore | Заказ №{kwargs["order_id"]}',
            'order': order,
            'cart': cart
        })
