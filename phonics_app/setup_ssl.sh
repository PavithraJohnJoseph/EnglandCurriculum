#!/bin/bash
# SSL Certificate Setup Script for Year 1 Phonics App
# This script sets up Let's Encrypt SSL certificates for production

set -e

echo "🔒 Setting up SSL Certificates for Year 1 Phonics App"
echo "====================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${YELLOW}Installing Certbot...${NC}"
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✓ Certbot installed${NC}"
fi

# Backup nginx configuration
echo -e "${YELLOW}Backing up nginx configuration...${NC}"
sudo cp /etc/nginx/sites-available/phonics_app /etc/nginx/sites-available/phonics_app.backup
echo -e "${GREEN}✓ Configuration backed up${NC}"

# Obtain SSL certificate
echo -e "${YELLOW}Obtaining SSL certificate for $DOMAIN...${NC}"
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

# Verify certificate
echo -e "${YELLOW}Verifying SSL certificate...${NC}"
if sudo certbot certificates | grep -q "$DOMAIN"; then
    echo -e "${GREEN}✓ SSL certificate obtained successfully${NC}"
else
    echo -e "${RED}✗ SSL certificate setup failed${NC}"
    exit 1
fi

# Set up auto-renewal
echo -e "${YELLOW}Setting up automatic certificate renewal...${NC}"
sudo crontab -l | grep -q certbot || (sudo crontab -l ; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

# Test nginx configuration
echo -e "${YELLOW}Testing nginx configuration...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}✓ Nginx configuration is valid${NC}"
    sudo systemctl reload nginx
    echo -e "${GREEN}✓ Nginx reloaded${NC}"
else
    echo -e "${RED}✗ Nginx configuration is invalid${NC}"
    exit 1
fi

echo -e "${GREEN}🎉 SSL setup complete!${NC}"
echo ""
echo "SSL Certificate Details:"
echo "- Certificate: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "- Private Key: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "- Auto-renewal: Configured (runs daily at noon)"
echo ""
echo "Next steps:"
echo "1. Update your .env.production file with HTTPS settings"
echo "2. Test HTTPS access: https://$DOMAIN"
echo "3. Set up SSL monitoring alerts"