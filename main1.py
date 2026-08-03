class Product:
    def __init__(self, name, category, price, quantity):
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity

    def change_price(self, new_price):
        self.price = new_price

    def change_quantity(self, new_quantity):
        self.quantity = new_quantity


class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.orders = []

    def add_order(self, order):
        self.orders.append(order)


class Order:
    def __init__(self):
        self.products = []
        self.total_price = 0

    def add_product(self, product):
        self.products.append(product)

    def calculate_total_price(self):
        self.total_price = 0

        for product in self.products:
            self.total_price += product.price

products = []

with open("products.txt", "r", encoding="utf-8") as file:

    for line in file:
        name, category, price, quantity = line.strip().split(";")

        product = Product(
            name,
            category,
            float(price),
            int(quantity)
        )

        products.append(product)
print("Список товарів:")

for product in products:
    print(
        product.name,
        product.category,
        product.price,
        product.quantity
    )


customer = Customer("Анастасія", "nasti4958@gmail.com")

order = Order()

order.add_product(products[0])
order.add_product(products[1])

order.calculate_total_price()

customer.add_order(order)

print("\nЗагальна сума замовлення:")
print(order.total_price)
#test