#!/bin/bash

# Get script's directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cwd="$(dirname "$SCRIPT_DIR")"  # cwd = current working directory, i.e., project root

# Move to the cwd (project root)
cd "$cwd" || exit

# Define the log file
LOG_FILE="/tmp/customer_cleanup_log.txt"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django shell command to delete inactive customers
DELETED_COUNT=$(python3 manage.py shell <<EOF
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.filter(order__isnull=True, created_at__lte=one_year_ago).distinct()
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log the result
if [ $? -eq 0 ]; then
    echo "[$TIMESTAMP] Deleted \$DELETED_COUNT inactive customers." >> \$LOG_FILE
else
    echo "[$TIMESTAMP] Error while cleaning customers." >> \$LOG_FILE
fi

