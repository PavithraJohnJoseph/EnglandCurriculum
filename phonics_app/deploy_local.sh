#!/bin/bash
# Local Docker Deployment Script for Testing
# Run this to test your app locally before production deployment

set -e

echo "🧪 Testing Year 1 Phonics App with Docker Locally"
echo "================================================="

# Check if .env exists (create from .env.production for testing)
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file for local testing..."
    cp .env.production .env
    # Modify for local testing
    sed -i 's/DEBUG=False/DEBUG=True/' .env
    sed -i 's/ALLOWED_HOSTS=.*/ALLOWED_HOSTS=localhost,127.0.0.1/' .env
    sed -i 's/SECURE_SSL_REDIRECT=True/SECURE_SSL_REDIRECT=False/' .env
    sed -i 's/CSRF_COOKIE_SECURE=True/CSRF_COOKIE_SECURE=False/' .env
    sed -i 's/SESSION_COOKIE_SECURE=True/SESSION_COOKIE_SECURE=False/' .env
    echo "✅ Local .env created"
fi

# Install Docker and Docker Compose if not present (Windows)
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker Desktop for Windows:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install it with Docker Desktop"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
echo "🐳 Building and starting containers..."
docker-compose build
docker-compose up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 20

# Check services
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
else
    echo "❌ Services failed to start. Check logs:"
    docker-compose logs
    exit 1
fi

# Run migrations
echo "🗄️ Running database migrations..."
docker-compose exec web python manage.py migrate

# Collect static files
echo "📄 Collecting static files..."
docker-compose exec web python manage.py collectstatic --noinput

# Run tests
echo "🧪 Running tests..."
docker-compose exec web python manage.py test

echo ""
echo "🎉 LOCAL DEPLOYMENT COMPLETE!"
echo "============================="
echo "Your app is running at: http://localhost"
echo ""
echo "Test these URLs:"
echo "  Health Check: http://localhost/health/"
echo "  Home Page: http://localhost/"
echo "  Login: http://localhost/login/"
echo "  Signup: http://localhost/signup/"
echo "  Plans: http://localhost/plan-selection/"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f web"
echo "  Stop: docker-compose down"
echo "  Restart: docker-compose restart"
echo ""
echo "When ready for production:"
echo "  1. Run: ./deploy_production.sh (on your server)"
echo "  2. Update ALLOWED_HOSTS with your domain"
echo "  3. Configure SSL certificates"