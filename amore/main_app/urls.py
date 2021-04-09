from django.urls import path

from main_app.views import MainPageView, CartPageView, OrderPageView, ProductDetailPageView

urlpatterns = [
    path('', MainPageView.as_view(), name='main'),
    path('cart/', CartPageView.as_view(), name='cart'),
    path('order/<str:order_id>/', OrderPageView.as_view(), name='order'),
    path('<str:category_slug>/<str:product_slug>/', ProductDetailPageView.as_view())
]
