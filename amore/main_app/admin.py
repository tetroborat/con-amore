from django.contrib import admin

from main_app.models import *

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Category)
admin.site.register(Promo)
admin.site.register(Pizza)