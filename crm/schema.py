import graphene
from graphene_django import DjangoObjectType
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db import transaction
import re
from .models import Customer, Product, Order
from datetime import datetime

# DjangoObjectTypes
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer

class ProductType(DjangoObjectType):
    class Meta:
        model = Product

class OrderType(DjangoObjectType):
    class Meta:
        model = Order

# Validation helper for phone
def validate_phone(phone):
    if phone is None:
        return True
    pattern = re.compile(r'^(\+?\d{1,3}[- ]?)?(\d{3}[- ]?\d{3}[- ]?\d{4})$')
    return pattern.match(phone)

# CreateCustomer mutation
class CreateCustomer(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=False)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, name, email, phone=None):
        try:
            validate_email(email)
        except ValidationError:
            return CreateCustomer(customer=None, message="Invalid email format.")

        if Customer.objects.filter(email=email).exists():
            return CreateCustomer(customer=None, message="Email already exists.")

        if phone and not validate_phone(phone):
            return CreateCustomer(customer=None, message="Invalid phone format.")

        customer = Customer(name=name, email=email, phone=phone)
        customer.save()

        return CreateCustomer(customer=customer, message="Customer created successfully.")

# BulkCreateCustomers mutation
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        created_customers = []
        errors = []

        with transaction.atomic():
            for idx, cust_data in enumerate(input):
                try:
                    validate_email(cust_data.email)
                    if Customer.objects.filter(email=cust_data.email).exists():
                        raise ValueError("Email already exists")
                    if cust_data.phone and not validate_phone(cust_data.phone):
                        raise ValueError("Invalid phone format")

                    customer = Customer(name=cust_data.name, email=cust_data.email, phone=cust_data.phone)
                    customer.save()
                    created_customers.append(customer)

                except Exception as e:
                    errors.append(f"Record {idx + 1}: {str(e)}")

        return BulkCreateCustomers(customers=created_customers, errors=errors)

# CreateProduct mutation
class CreateProduct(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        price = graphene.Float(required=True)
        stock = graphene.Int(required=False)

    product = graphene.Field(ProductType)
    message = graphene.String()

    def mutate(self, info, name, price, stock=0):
        if price <= 0:
            return CreateProduct(product=None, message="Price must be positive.")
        if stock < 0:
            return CreateProduct(product=None, message="Stock cannot be negative.")

        product = Product(name=name, price=price, stock=stock)
        product.save()

        return CreateProduct(product=product, message="Product created successfully.")

# CreateOrder mutation
class CreateOrder(graphene.Mutation):
    class Arguments:
        customer_id = graphene.ID(required=True)
        product_ids = graphene.List(graphene.ID, required=True)
        order_date = graphene.DateTime(required=False)

    order = graphene.Field(OrderType)
    message = graphene.String()

    def mutate(self, info, customer_id, product_ids, order_date=None):
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return CreateOrder(order=None, message="Invalid customer ID.")

        if not product_ids:
            return CreateOrder(order=None, message="At least one product must be selected.")

        products = Product.objects.filter(pk__in=product_ids)
        if len(products) != len(product_ids):
            return CreateOrder(order=None, message="One or more invalid product IDs.")

        total_amount = sum(p.price for p in products)

        if order_date is None:
            order_date = datetime.now()

        order = Order(customer=customer, order_date=order_date, total_amount=total_amount)
        order.save()
        order.products.set(products)
        order.save()

        return CreateOrder(order=order, message="Order created successfully.")

# ✅ UpdateLowStockProducts mutation
class UpdateLowStockProducts(graphene.Mutation):
    updated_products = graphene.List(graphene.String)
    success = graphene.String()

    def mutate(self, info):
        # ✅ Queries products with stock < 10
        low_stock_products = Product.objects.filter(stock__lt=10)
        updated_names = []

        for product in low_stock_products:
            # ✅ Increments their stock by 10
            product.stock += 10
            product.save()
            updated_names.append(f"{product.name} ({product.stock})")

        # ✅ Returns a list of updated products and a success message
        return UpdateLowStockProducts(
            updated_products=updated_names,
            success="Stock updated successfully"
        )

# ✅ Mutation class
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()

# Query class
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

schema = graphene.Schema(query=Query, mutation=Mutation)

