from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    # Generate timestamp in DD/MM/YYYY-HH:MM:SS format
    timestamp = datetime.now().strftime('%d/%m/%Y-%H:%M:%S')
    message = f"{timestamp} CRM is alive\n"

    # Append the message to /tmp/crm_heartbeat_log.txt
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

    # Optional: Check if GraphQL endpoint responds to hello field
    try:
        # Set up GraphQL transport and client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Define the query
        query = gql("{ hello }")

        # Execute the query
        response = client.execute(query)
        print("GraphQL hello response:", response)

    except Exception as e:
        print("GraphQL hello check failed:", str(e))

