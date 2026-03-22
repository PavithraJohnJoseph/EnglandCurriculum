#!/bin/bash
# Security Monitoring Script for Year 1 Phonics App
# Run this script periodically to check security status

set -e

echo "🛡️  Year 1 Phonics App - Security Check"
echo "======================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ISSUES_FOUND=0

# Check SSL certificate expiry
echo -e "${YELLOW}Checking SSL certificate expiry...${NC}"
if command -v openssl &> /dev/null; then
    # This would need to be run on the server with actual certificates
    echo "SSL certificate check: Run on production server with certificates"
else
    echo -e "${YELLOW}⚠️  OpenSSL not found - run on production server${NC}"
fi

# Check file permissions
echo -e "${YELLOW}Checking file permissions...${NC}"
if [ -f ".env.production" ]; then
    PERMS=$(stat -c "%a" .env.production 2>/dev/null || echo "unknown")
    if [ "$PERMS" = "600" ]; then
        echo -e "${GREEN}✓ .env.production has correct permissions (600)${NC}"
    else
        echo -e "${RED}✗ .env.production permissions should be 600, currently $PERMS${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠️  .env.production not found${NC}"
fi

# Check database backup
echo -e "${YELLOW}Checking database backups...${NC}"
if [ -d "/var/backups/phonics_app" ]; then
    BACKUP_COUNT=$(find /var/backups/phonics_app -name "*.sql" -mtime -1 | wc -l)
    if [ "$BACKUP_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Recent database backup found ($BACKUP_COUNT files < 24h old)${NC}"
    else
        echo -e "${RED}✗ No recent database backups found${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠️  Backup directory not found - run on production server${NC}"
fi

# Check Django SECRET_KEY strength
echo -e "${YELLOW}Checking Django SECRET_KEY...${NC}"
if [ -f ".env.production" ]; then
    SECRET_KEY=$(grep SECRET_KEY .env.production | cut -d'=' -f2-)
    if [ ${#SECRET_KEY} -ge 50 ]; then
        echo -e "${GREEN}✓ SECRET_KEY is sufficiently long (${#SECRET_KEY} characters)${NC}"
    else
        echo -e "${RED}✗ SECRET_KEY is too short (${#SECRET_KEY} characters, should be >= 50)${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠️  .env.production not found${NC}"
fi

# Check DEBUG mode
echo -e "${YELLOW}Checking DEBUG mode...${NC}"
if [ -f ".env.production" ]; then
    DEBUG=$(grep "^DEBUG=" .env.production | cut -d'=' -f2)
    if [ "$DEBUG" = "False" ]; then
        echo -e "${GREEN}✓ DEBUG is disabled in production${NC}"
    else
        echo -e "${RED}✗ DEBUG should be False in production${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    fi
else
    echo -e "${YELLOW}⚠️  .env.production not found${NC}"
fi

# Check ALLOWED_HOSTS
echo -e "${YELLOW}Checking ALLOWED_HOSTS...${NC}"
if [ -f ".env.production" ]; then
    ALLOWED_HOSTS=$(grep ALLOWED_HOSTS .env.production | cut -d'=' -f2-)
    if [[ $ALLOWED_HOSTS == *"localhost"* ]]; then
        echo -e "${RED}✗ ALLOWED_HOSTS should not include localhost in production${NC}"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        echo -e "${GREEN}✓ ALLOWED_HOSTS configured for production${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env.production not found${NC}"
fi

# Summary
echo ""
echo "🔍 Security Check Summary:"
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks passed!${NC}"
else
    echo -e "${RED}✗ $ISSUES_FOUND security issues found${NC}"
fi

echo ""
echo "📋 Security Checklist:"
echo "□ SSL certificate valid and not expiring soon"
echo "□ File permissions set correctly"
echo "□ Database backups running regularly"
echo "□ SECRET_KEY is strong and unique"
echo "□ DEBUG=False in production"
echo "□ ALLOWED_HOSTS configured correctly"
echo "□ Security headers enabled"
echo "□ Rate limiting configured"
echo "□ Admin panel protected"
echo "□ Regular security updates applied"

exit $ISSUES_FOUND