from collections import UserDict



class Basket(UserDict):
    changed = False

    def add(self, quantity=0, option=None, set_=False):
        self.changed = True
        id_ = str(option.product.id)
        option = str(option.id)
        self.setdefault(id_, {})
        self[id_].setdefault(option, 0)

        if set_:
            self[id_][option] = quantity
        else:
            self[id_][option] += quantity

        if self[id_][option] <= 0:
            del self[id_][option]
            if not self[id_]:
                del self[id_]
            return 0
        else:
            return self[id_][option]

    @property
    def total_count(self):
        return sum(x for product, options in self.items() for _, x in options.items())

    @property
    def total_price(self):
        prices = {str(id_): price for id_, price in
                  Product.objects.filter(id__in=self.keys()).values_list('id', 'price')}
        return sum(x * prices[product] for product, options in self.items() for _, x in options.items())

    def cost(self, option):
        price = option.product.price
        return self.count_option(option) * price

    def count_option(self, option):
        product_id = str(option.product.id)
        option_id = str(option.id)
        return self.get(product_id, {}).get(option_id, 0)

    def flush(self):
        self.changed = True
        for key in list(self):
            del self[key]

    def build_order(self, order):
        items = []
        for product_id, data in self.items():
            product = Product.objects.get(id=product_id)

            for option_id, quantity in data.items():
                if quantity == 0:
                    continue
                option = None
                if option_id != '0':
                    option = ProductOption.objects.get(id=option_id)
                items.append(
                    Item(order=order, option=option, quantity=quantity, product=product)
                )
        order.items.bulk_create(items)
        self.flush()
        return order

    def fix(self):
        """Фиксит корзину на случай, если опции удалили, а они находятся в корзине"""
        ids = self.keys()
        exist_in_db = (Product.objects
                       .filter(id__in=ids, options__in_stock=True, options__show=True)
                       .values_list('id', flat=True))
        to_remove = set(ids) - set(str(x) for x in exist_in_db)
        for id_ in to_remove:
            del self[id_]
        if to_remove:
            self.changed = True

    def to_dict(self):
        return dict(self)