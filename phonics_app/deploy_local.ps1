# Local Docker Deployment Script for Windows
# Run this to test your app locally before production deployment

Write-Host "🧪 Testing Year 1 Phonics App with Docker Locally" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green

# Check if .env exists (create from .env.production for testing)
if (!(Test-Path ".env")) {
    Write-Host "📋 Creating .env file for local testing..." -ForegroundColor Yellow
    Copy-Item ".env.production" ".env"

    # Modify for local testing
    (Get-Content ".env") -replace "DEBUG=False", "DEBUG=True" | Set-Content ".env"
    (Get-Content ".env") -replace "ALLOWED_HOSTS=.*", "ALLOWED_HOSTS=localhost,127.0.0.1" | Set-Content ".env"
    (Get-Content ".env") -replace "SECURE_SSL_REDIRECT=True", "SECURE_SSL_REDIRECT=False" | Set-Content ".env"
    (Get-Content ".env") -replace "CSRF_COOKIE_SECURE=True", "CSRF_COOKIE_SECURE=False" | Set-Content ".env"
    (Get-Content ".env") -replace "SESSION_COOKIE_SECURE=True", "SESSION_COOKIE_SECURE=False" | Set-Content ".env"

    Write-Host "✅ Local .env created" -ForegroundColor Green
}

# Check Docker
if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker not found. Please install Docker Desktop for Windows:" -ForegroundColor Red
    Write-Host "   https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}

if (!(Get-Command docker-compose -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Docker Compose not found. Please install it with Docker Desktop" -ForegroundColor Red
    exit 1
}

# Stop any existing containers
Write-Host "🛑 Stopping existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start services
Write-Host "🐳 Building and starting containers..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start containers!" -ForegroundColor Red
    exit 1
}

# Wait for services
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Check services
$services = docker-compose ps
if ($services -match "Up") {
    Write-Host "✅ Services are running!" -ForegroundColor Green
} else {
    Write-Host "❌ Services failed to start. Check logs:" -ForegroundColor Red
    docker-compose logs
    exit 1
}

# Run migrations
Write-Host "🗄️ Running database migrations..." -ForegroundColor Yellow
docker-compose exec web python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    exit 1
}

# Collect static files
Write-Host "📄 Collecting static files..." -ForegroundColor Yellow
docker-compose exec web python manage.py collectstatic --noinput
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Static files collection failed!" -ForegroundColor Red
    exit 1
}

# Run tests
Write-Host "🧪 Running tests..." -ForegroundColor Yellow
docker-compose exec web python manage.py test
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 LOCAL DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
Write-Host "Your app is running at: http://localhost" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test these URLs:" -ForegroundColor Cyan
Write-Host "  Health Check: http://localhost/health/" -ForegroundColor White
Write-Host "  Home Page: http://localhost/" -ForegroundColor White
Write-Host "  Login: http://localhost/login/" -ForegroundColor White
Write-Host "  Signup: http://localhost/signup/" -ForegroundColor White
Write-Host "  Plans: http://localhost/plan-selection/" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs: docker-compose logs -f web" -ForegroundColor White
Write-Host "  Stop: docker-compose down" -ForegroundColor White
Write-Host "  Restart: docker-compose restart" -ForegroundColor White
Write-Host ""
Write-Host "When ready for production:" -ForegroundColor Green
Write-Host "  1. Run: .\deploy_production.ps1 (on your server)" -ForegroundColor White
Write-Host "  2. Update ALLOWED_HOSTS with your domain" -ForegroundColor White
Write-Host "  3. Configure SSL certificates" -ForegroundColor White