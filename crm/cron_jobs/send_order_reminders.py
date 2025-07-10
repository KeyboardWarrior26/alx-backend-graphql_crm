#!/usr/bin/env python3

import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Setup logging
log_file = "/tmp/order_reminders_log.txt"
logging.basicConfig(filename=log_file, level=logging.INFO)

# Timestamp for log entries
timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

# Define the GraphQL query
query = gql("""
query GetRecentOrders {
  orders(orderDate_Gte: "%s") {
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
""" % (datetime.date.today() - datetime.timedelta(days=7)))

# Set up the GraphQL client
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=False)

# Run the query and log the output
try:
    result = client.execute(query)
    orders = result["orders"]["edges"]
    
    for order in orders:
        order_id = order["node"]["id"]
        email = order["node"]["customer"]["email"]
        logging.info(f"{timestamp} Order ID: {order_id}, Email: {email}")

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"{timestamp} Error: {str(e)}")
    print("Failed to process order reminders.")
