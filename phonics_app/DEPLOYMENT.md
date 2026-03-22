# Production Deployment Guide

## Overview
This guide covers deploying the Year 1 Phonics App to production using Docker and Docker Compose.

## Prerequisites
- Docker and Docker Compose installed
- Domain name (optional for HTTPS)
- SSL certificate (for HTTPS)
- Environment variables configured
- Stripe accounts (for payments)

## Phase 1: Environment Setup

### 1. Create Production .env File
```bash
cp .env.example .env.production
```

Edit `.env.production` with production values:
```
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@postgres:5432/phonics_db
POSTGRES_DB=phonics_db
POSTGRES_USER=phonics_user
POSTGRES_PASSWORD=<secure-password>

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Stripe
STRIPE_PUBLIC_KEY=pk_live_your_key
STRIPE_SECRET_KEY=sk_live_your_key
```

### 2. Generate Secure Secret Key
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

## Phase 2: Build and Deploy

### 1. Build Docker Image
```bash
docker build -t phonics-app:latest .
```

### 2. Start Services
```bash
# Using environment file
docker-compose --env-file .env.production up -d
```

### 3. Run Migrations
```bash
docker exec phonics_app python manage.py migrate
```

### 4. Setup Initial Data
```bash
docker exec phonics_app python manage.py setup_initial_data
```

### 5. Create Superuser
```bash
docker exec -it phonics_app python manage.py createsuperuser
```

## Phase 3: SSL/HTTPS Setup

### 1. Using Let's Encrypt with Certbot
```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Update nginx.conf with certificate paths:
# ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
# ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# Mount certificates in docker-compose:
# volumes:
#   - /etc/letsencrypt:/etc/letsencrypt
```

### 2. Auto-renewal Setup
```bash
# Create renewal cron job
0 3 * * * certbot renew --quiet && docker-compose restart nginx
```

## Phase 4: Monitoring & Maintenance

### 1. View Logs
```bash
# Web app logs
docker logs -f phonics_app

# PostgreSQL logs
docker logs -f phonics_db

# Nginx logs
docker logs -f phonics_nginx
```

### 2. Database Backup
```bash
# Manual backup
docker exec phonics_db pg_dump -U phonics_user phonics_db > backup.sql

# Restore backup
docker exec -i phonics_db psql -U phonics_user phonics_db < backup.sql

# Automated backup (cron)
0 2 * * * docker exec phonics_db pg_dump -U phonics_user phonics_db | gzip > /backups/phonics_$(date +\%Y\%m\%d).sql.gz
```

### 3. Check Application Health
```bash
curl https://yourdomain.com/health/
```

### 4. Monitor Performance
```bash
# Check Docker resource usage
docker stats

# Check database connections
docker exec phonics_db psql -U phonics_user -d phonics_db -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

## Phase 5: Troubleshooting

### Application not starting
```bash
# Check logs
docker logs phonics_app

# Verify environment variables
docker exec phonics_app env | sort
```

### Database connection issues
```bash
# Test database connection
docker exec phonics_app python manage.py dbshell

# Check database status
docker-compose ps
```

### Static files not loading
```bash
# Collect static files
docker exec phonics_app python manage.py collectstatic --noinput

# Check nginx serving static files
curl -I https://yourdomain.com/static/core/css/styles.css
```

## Phase 6: Updates & Scaling

### 1. Update Application
```bash
# Pull latest code
git pull origin main

# Rebuild image
docker build -t phonics-app:latest .

# Run migrations
docker exec phonics_app python manage.py migrate

# Restart service
docker-compose restart web
```

### 2. Scale Application (if using Docker Swarm)
```bash
docker service scale phonics_app=3
```

## Phase 7: Security Checklist

- [ ] DEBUG=False in production
- [ ] SECRET_KEY is unique and secure
- [ ] ALLOWED_HOSTS is correctly configured
- [ ] SSL/HTTPS is enabled
- [ ] Database password is strong
- [ ] Email credentials are stored securely
- [ ] Regular backups are scheduled
- [ ] Log monitoring is in place
- [ ] Access logs are reviewed regularly
- [ ] Security updates are applied promptly

## Support & Maintenance

- Regular security updates
- Database optimization
- Performance monitoring
- Regular backups
- SSL certificate renewal (auto with certbot)
- Keep Docker images updated

## Quick Reference Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View status
docker-compose ps

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec web python manage.py <command>

# Rebuild container
docker-compose build --no-cache
```
