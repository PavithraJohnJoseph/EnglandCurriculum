#!/bin/bash
# Production Deployment Script for Year 1 Phonics App
# Run this on your production server

set -e

echo "🚀 Starting Year 1 Phonics App Production Deployment"
echo "=================================================="

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ Error: .env.production file not found!"
    echo "Please copy .env.production.template to .env.production and configure it"
    exit 1
fi

# Load environment variables
set -a
source .env.production
set +a

echo "✅ Environment file loaded"

# Install Docker and Docker Compose if not present
if ! command -v docker &> /dev/null; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    echo "✅ Docker installed"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p media staticfiles logs
echo "✅ Directories created"

# Build and start services
echo "🐳 Building and starting Docker containers..."
docker-compose down 2>/dev/null || true
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

# Run database migrations
echo "🗄️ Running database migrations..."
docker-compose exec web python manage.py migrate

# Collect static files
echo "📄 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser (optional)
echo "👤 Do you want to create a Django superuser? (y/n)"
read -r create_superuser
if [[ $create_superuser =~ ^[Yy]$ ]]; then
    docker-compose exec web python manage.py createsuperuser
fi

# Run tests
echo "🧪 Running tests..."
docker-compose exec web python manage.py test

# Setup SSL (if domain is configured)
if [ ! -z "$DOMAIN" ]; then
    echo "🔒 Setting up SSL certificates..."
    ./setup_ssl.sh
fi

# Final health check
echo "🏥 Running final health check..."
if curl -f http://localhost/health/ > /dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "⚠️ Health check failed - check application logs"
fi

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "Your app is running at: http://your-server-ip"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Restart: docker-compose restart"
echo "  Stop: docker-compose down"
echo "  Update: docker-compose pull && docker-compose up -d"
echo ""
echo "Don't forget to:"
echo "  1. Update ALLOWED_HOSTS in .env.production with your domain"
echo "  2. Configure DNS to point to your server"
echo "  3. Set up SSL certificates (run ./setup_ssl.sh)"
echo "  4. Update Stripe keys to production when ready"