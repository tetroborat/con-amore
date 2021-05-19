from django.http import JsonResponse, HttpResponseRedirect
from django.utils.safestring import mark_safe
from amore.settings import TOKEN, MY_ID
from .cart import Cart as SessionCart
from django.shortcuts import render
from django.contrib import messages
from django.views import View
from datetime import datetime
from main_app.models import *
from .models import Product
from telepot import Bot


telegramBot = Bot(TOKEN)


def send_message(text):
    telegramBot.sendMessage(MY_ID, text, parse_mode="HTML")


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
        if SessionCart(request).get_total_price() == 0:
            return HttpResponseRedirect('/')
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
            time_begin=datetime.now(timezone.utc),
            customer=request.POST.get('input_name'),
            number_customer=request.POST.get('input_phone_number'),
            address=request.POST.get('input_address') if request.POST.get('check_address') != 'on' else 'Самовывоз',
            cart=cart,
            total_price=cart.get_total_price(),
            comment=request.POST.get('input_comment')
        )
        order.save()
        message = f'<a href="con-amore.herokuapp.com/order_detail/{order.number_customer}/{order.pk}/"><b>Заказ №{order.pk}</b></a>\n\n' \
                  f'{order.cart}\n' \
                  f'<b>Итого: {order.total_price} ₽</b>\n\n' \
                  f'{order.customer}\n' \
                  f'{order.address}\n' \
                  f'<a href="tel:{order.number_customer}">{order.number_customer}</a>'
        if order.comment != '':
            message += f'\nКомментарий: {order.comment}'
        send_message(message)
        messages.success(request, mark_safe(
            f'Скоро мы позвоним Вам!<br>Заказ <a href="{order.get_url()}" class="alert-link">номер №{order.pk}</a> поступил в обработку.'))
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
        order = Order.objects.filter(id=int(kwargs['order_id']), number_customer=kwargs['number'])
        if not order.exists():
            return render(request, 'order_detail_page.html', {
                'title': 'Con Amore | Заказ не найден',
                'error': 'Такого заказа не существует'
            })
        else:
            order = order.first()
            cart = [
                {
                    'product': Product.objects.get(name=item_product[item_product.find('x') + 2: item_product.find('(') - 1]),
                    'price': item_product[item_product.find('(') + 1: item_product.find('₽') - 1],
                    'quantity': item_product.split(' ')[0]
                }
                if 'см' not in item_product else
                {
                    'product': Product.objects.get(name=item_product[item_product.find('x') + 2: item_product.find('см') - 5]),
                    'size': item_product[item_product.find('см') - 2: item_product.find('см')],
                    'price': item_product[item_product.find('(') + 1: item_product.find('₽') - 1],
                    'quantity': item_product.split(' ')[0]
                }
                for item_product in order.cart.split('\n')[:-1]
            ]
            return render(request, 'order_detail_page.html', {
                'title': f'Con Amore | Заказ №{kwargs["order_id"]}',
                'order': order,
                'cart': cart,
                'total_price': int(order.total_price)
            })
