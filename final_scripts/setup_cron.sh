#!/bin/bash

# Get absolute path of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH="/usr/bin/python3"
SCRIPT_PATH="$SCRIPT_DIR/main.py"
LOG_FILE="$SCRIPT_DIR/cron_log.txt"
OUTPUT_FILE="$SCRIPT_DIR/esg_pdf_links.txt"

# Add cron job (runs every Monday at 3 AM)
(crontab -l 2>/dev/null; echo "0 1 * * 4 $PYTHON_PATH $SCRIPT_PATH >> $LOG_FILE 2>&1") | crontab -

echo "Cron job added successfully!"
echo "Logs will be stored in: $LOG_FILE"
echo "PDF links will be stored in: $OUTPUT_FILE"


## To run the file: 
# chmod +x setup_cron.sh 
# ./setup_cron.sh
