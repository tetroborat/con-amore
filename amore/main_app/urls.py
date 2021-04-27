from django.urls import path

from main_app.views import *

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('order/', OrderPageView.as_view(), name='order'),
    path('modal_cart/', CartModalView.as_view(), name='modal_cart'),
    path('add_product_in_cart/', AddProductInCart, name='add_product_in_cart'),
    path('clear_cart/', ClearCart, name='clear_cart'),
    path('remove_product_from_cart/', RemoveProductFromCart, name='remove_product_from_cart'),
    path('del_product_from_cart/', DeleteProductFromCart, name='del_product_from_cart'),
    path('products_in_cart_images/', ProductsInCartImagesView.as_view(), name='products_in_cart_images'),
]
