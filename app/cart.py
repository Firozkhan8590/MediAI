class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}
        self.cart = cart

    def add(self, product, quantity=1):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] += quantity
        else:
            self.cart[product_id] = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity
            }
        self.save()

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def update(self, product, quantity):
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = quantity
            self.save()

    def clear(self):
        self.session["cart"] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        for product_id,item in self.cart.items():
            item['id'] = product_id
            item['total'] = float(item['price']) * item['quantity']
            yield item

    def total_price(self):
        return sum(float(item['price']) * item['quantity'] for item in self.cart.values())
    
    def count(self):
        return sum(item['quantity'] for item in self.cart.values())
