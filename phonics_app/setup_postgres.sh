#!/bin/bash
# PostgreSQL Database Setup Script for Year 1 Phonics App
# Run this on your production server with sudo privileges

set -e

echo "🐘 Setting up PostgreSQL Database for Year 1 Phonics App"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root or with sudo
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# 1. Install PostgreSQL if not installed
echo -e "\n${YELLOW}1. Checking PostgreSQL installation...${NC}"
if ! command -v psql &> /dev/null; then
    echo "Installing PostgreSQL..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
    echo -e "${GREEN}✓ PostgreSQL installed${NC}"
else
    echo -e "${GREEN}✓ PostgreSQL already installed${NC}"
fi

# 2. Start PostgreSQL service
echo -e "\n${YELLOW}2. Starting PostgreSQL service...${NC}"
sudo systemctl start postgresql
sudo systemctl enable postgresql
echo -e "${GREEN}✓ PostgreSQL service started${NC}"

# 3. Create database and user
echo -e "\n${YELLOW}3. Creating database and user...${NC}"
sudo -u postgres psql << EOF
-- Create user
CREATE USER phonics_user WITH PASSWORD 'secure_password_123';

-- Create database
CREATE DATABASE phonics_db OWNER phonics_user;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE phonics_db TO phonics_user;

-- Set up extensions
\c phonics_db
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
EOF
echo -e "${GREEN}✓ Database and user created${NC}"

# 4. Configure PostgreSQL for production
echo -e "\n${YELLOW}4. Configuring PostgreSQL for production...${NC}"
sudo tee /etc/postgresql/13/main/conf.d/phonics.conf > /dev/null << EOF
# Phonics App PostgreSQL Configuration
listen_addresses = 'localhost'
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 4MB
min_wal_size = 1GB
max_wal_size = 4GB
EOF
echo -e "${GREEN}✓ PostgreSQL configured${NC}"

# 5. Restart PostgreSQL
echo -e "\n${YELLOW}5. Restarting PostgreSQL...${NC}"
sudo systemctl restart postgresql
echo -e "${GREEN}✓ PostgreSQL restarted${NC}"

# 6. Test connection
echo -e "\n${YELLOW}6. Testing database connection...${NC}"
if PGPASSWORD=secure_password_123 psql -h localhost -U phonics_user -d phonics_db -c "SELECT version();" > /dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Database connection failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}🎉 PostgreSQL setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Update your .env.production file with the correct database credentials"
echo "2. Run database migrations: python manage.py migrate"
echo "3. Set up automated backups (see backup script)"
echo "4. Configure monitoring and alerts"