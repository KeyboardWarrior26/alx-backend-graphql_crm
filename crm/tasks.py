from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        query = gql("""
        {
          customers { id }
          orders { id totalAmount }
        }
        """)

        response = client.execute(query)
        total_customers = len(response["customers"])
        total_orders = len(response["orders"])
        total_revenue = sum(order["totalAmount"] for order in response["orders"])

        report = f"{timestamp} - Report: {total_customers} customers, {total_orders} orders, R{total_revenue:.2f}\n"

        with open(log_file, "a") as f:
            f.write(report)

        print("CRM report generated.")
    except Exception as e:
        print("Failed to generate CRM report:", str(e))
