import os
import django
from datetime import datetime
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order

def seed_customers():
    customers = [
        {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
        {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
        {"name": "Carol", "email": "carol@example.com", "phone": None},
    ]

    for cust in customers:
        if not Customer.objects.filter(email=cust["email"]).exists():
            Customer.objects.create(**cust)
    print("Seeded customers.")

def seed_products():
    products = [
        {"name": "Laptop", "price": 999.99, "stock": 10},
        {"name": "Smartphone", "price": 499.99, "stock": 20},
        {"name": "Headphones", "price": 199.99, "stock": 30},
    ]

    for prod in products:
        if not Product.objects.filter(name=prod["name"]).exists():
            Product.objects.create(**prod)
    print("Seeded products.")

def seed_orders():
    # Create one order for Alice with Laptop and Smartphone
    alice = Customer.objects.filter(email="alice@example.com").first()
    laptop = Product.objects.filter(name="Laptop").first()
    smartphone = Product.objects.filter(name="Smartphone").first()

    if alice and laptop and smartphone:
        # Check if order already exists to avoid duplicates
        existing_order = Order.objects.filter(customer=alice).first()
        if not existing_order:
            order = Order(customer=alice)
            order.save()
            order.products.set([laptop, smartphone])
            order.total_amount = laptop.price + smartphone.price
            order.order_date = timezone.now()
            order.save()
            print("Seeded orders.")
        else:
            print("Order for Alice already exists.")
    else:
        print("Could not seed orders — missing data.")

if __name__ == "__main__":
    seed_customers()
    seed_products()
    seed_orders()
