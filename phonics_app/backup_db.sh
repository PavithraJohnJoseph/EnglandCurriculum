#!/bin/bash
# Database Backup Script for Year 1 Phonics App
# Run this daily via cron: 0 2 * * * /path/to/backup_db.sh

set -e

echo "💾 Year 1 Phonics App - Database Backup"
echo "========================================"

# Configuration
DB_HOST="localhost"
DB_USER="phonics_user"
DB_NAME="phonics_db"
BACKUP_DIR="/var/backups/phonics_app"
RETENTION_DAYS=30

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create backup directory if it doesn't exist
if [ ! -d "$BACKUP_DIR" ]; then
    sudo mkdir -p "$BACKUP_DIR"
    sudo chown postgres:postgres "$BACKUP_DIR"
fi

# Generate timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/phonics_db_$TIMESTAMP.sql"

# Create backup
echo -e "${YELLOW}Creating database backup...${NC}"
PGPASSWORD=secure_password_123 pg_dump \
    -h "$DB_HOST" \
    -U "$DB_USER" \
    -d "$DB_NAME" \
    --no-password \
    --format=custom \
    --compress=9 \
    --verbose \
    > "$BACKUP_FILE"

echo -e "${GREEN}✓ Backup created: $BACKUP_FILE${NC}"

# Set permissions
sudo chown postgres:postgres "$BACKUP_FILE"
sudo chmod 600 "$BACKUP_FILE"

# Clean up old backups
echo -e "${YELLOW}Cleaning up old backups...${NC}"
find "$BACKUP_DIR" -name "phonics_db_*.sql" -mtime +$RETENTION_DAYS -delete
echo -e "${GREEN}✓ Old backups cleaned up${NC}"

# Verify backup
echo -e "${YELLOW}Verifying backup...${NC}"
if pg_restore --list "$BACKUP_FILE" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backup verification successful${NC}"
else
    echo -e "${RED}✗ Backup verification failed${NC}"
    exit 1
fi

# Log backup completion
echo "$(date): Database backup completed successfully - $BACKUP_FILE" >> /var/log/phonics_backup.log

echo -e "${GREEN}🎉 Database backup complete!${NC}"

# Optional: Upload to cloud storage (uncomment and configure)
# aws s3 cp "$BACKUP_FILE" s3://your-backup-bucket/phonics_backups/
# az storage blob upload --account-name yourstorage --container-name backups --name "$(basename $BACKUP_FILE)" --file "$BACKUP_FILE"