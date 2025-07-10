from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Heartbeat Cron Task
def log_crm_heartbeat():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql("{ hello }")
        response = client.execute(query)
        print("GraphQL hello response:", response)
    except Exception as e:
        print("GraphQL hello check failed:", str(e))


# Order Reminder Cron Task
def send_order_reminders():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = "/tmp/order_reminders_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("""
        {
          orders(filter: {orderDate_Gte: "%s"}) {
            edges {
              node {
                id
                customer {
                  email
                }
              }
            }
          }
        }
        """ % (datetime.now().date().isoformat()))

        response = client.execute(query)
        orders = response["orders"]["edges"]

        with open(log_file, "a") as f:
            f.write(f"{timestamp} Order reminders:\n")
            for edge in orders:
                order = edge["node"]
                f.write(f"  - Order ID: {order['id']}, Customer Email: {order['customer']['email']}\n")

        print("Order reminders processed!")

    except Exception as e:
        print("Failed to send order reminders:", str(e))


# Low Stock Restock Cron Task
def update_low_stock():
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        mutation = gql("""
        mutation {
          updateLowStockProducts {
            updatedProducts
            success
          }
        }
        """)

        response = client.execute(mutation)
        updated_products = response["updateLowStockProducts"]["updatedProducts"]

        with open(log_file, "a") as f:
            f.write(f"{timestamp} Updated products:\n")
            for product in updated_products:
                f.write(f"  - {product}\n")

        print("Low stock products updated.")

    except Exception as e:
        print("Failed to update low stock products:", str(e))

