#!/bin/bash
# Quick start script for Year 1 Phonics App

set -e

echo "🚀 Year 1 Phonics App - Quick Start"
echo "===================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Create virtual environment
echo -e "\n${YELLOW}1. Setting up Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# 2. Activate virtual environment
echo -e "\n${YELLOW}2. Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# 3. Install dependencies
echo -e "\n${YELLOW}3. Installing dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# 4. Run migrations
echo -e "\n${YELLOW}4. Running database migrations...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrations completed${NC}"

# 5. Setup initial data
echo -e "\n${YELLOW}5. Setting up initial data...${NC}"
python manage.py setup_initial_data
echo -e "${GREEN}✓ Initial data created${NC}"

# 6. Collect static files
echo -e "\n${YELLOW}6. Collecting static files...${NC}"
python manage.py collectstatic --noinput -q
echo -e "${GREEN}✓ Static files collected${NC}"

# 7. Summary
echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Create a superuser: python manage.py createsuperuser"
echo "2. Start development server: python manage.py runserver"
echo "3. Visit http://127.0.0.1:8000"
echo "4. Admin panel: http://127.0.0.1:8000/admin"
echo ""
echo "For testing:"
echo "  pytest                    # Run all tests"
echo "  pytest --cov=core         # Run with coverage"
echo ""
echo "For production deployment:"
echo "  See DEPLOYMENT.md for Docker setup"
