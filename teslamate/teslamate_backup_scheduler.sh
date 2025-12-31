#!/bin/bash

# --- Configuration ---
BACKUP_DIR="~/dockers/teslamate/backups"
DB_CONTAINER="teslamate-database-1"
GF_CONTAINER="teslamate-grafana-1"

# --- Create directory if it doesn't exist ---
mkdir -p $BACKUP_DIR



# ----------------------------------
#
#              TESLAMATE 
#             (db backup)
#
# ----------------------------------
# --- 1. Rotate Teslamate Database Backups ---
# Delete the 2-week-old backup (if it exists)
rm -f $BACKUP_DIR/teslamate.bck.2

# Move last week's backup (1) to be the 2-week-old backup (2)
mv -f $BACKUP_DIR/teslamate.bck.1 $BACKUP_DIR/teslamate.bck.2

# Create the new "this week" backup (1)
echo "Backing up Teslamate database..."
docker exec $DB_CONTAINER pg_dump -U teslamate teslamate > $BACKUP_DIR/teslamate.bck.1





# ----------------------------------
#
#              GRAFANA 
#         (settings backup)
#
# ----------------------------------
# --- 2. Rotate Grafana Config Backups ---
# Delete the 2-week-old backup
rm -f $BACKUP_DIR/grafana.tar.gz.2

# Move last week's backup
mv -f $BACKUP_DIR/grafana.tar.gz.1 $BACKUP_DIR/grafana.tar.gz.2

# Create the new "this week" backup
echo "Backing up Grafana data..."
docker exec $GF_CONTAINER tar -czf - /var/lib/grafana > $BACKUP_DIR/grafana.tar.gz.1

echo "Backup complete!"