import datetime
import requests

def log_crm_heartbeat():
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    
    try:
        # Optional GraphQL hello query
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': '{ hello }'},
            timeout=5
        )
        if response.ok:
            message = f"{timestamp} CRM is alive (GraphQL OK)\n"
        else:
            message = f"{timestamp} CRM is alive (GraphQL ERROR)\n"
    except Exception:
        message = f"{timestamp} CRM is alive (GraphQL TIMEOUT)\n"

    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

def update_low_stock():
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_path = "/tmp/low_stock_updates_log.txt"

    mutation = '''
    mutation {
        updateLowStockProducts {
            message
            updatedProducts {
                name
                stock
            }
        }
    }
    '''

    try:
        response = requests.post(
            'http://localhost:8000/graphql',
            json={'query': mutation},
            timeout=10
        )
        if response.ok:
            data = response.json().get('data', {}).get('updateLowStockProducts', {})
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} - {data.get('message')}\n")
                for product in data.get('updatedProducts', []):
                    log_file.write(f"→ {product['name']} stock: {product['stock']}\n")
        else:
            with open(log_path, 'a') as log_file:
                log_file.write(f"{timestamp} - GraphQL ERROR {response.status_code}: {response.text}\n")
    except Exception as e:
        with open(log_path, 'a') as log_file:
            log_file.write(f"{timestamp} - Exception occurred: {str(e)}\n")

'''
    Add and Run the Cron Job
    Register the cron job with Django:
    python manage.py crontab add
    Confirm it's working:
    python manage.py crontab show
'''
