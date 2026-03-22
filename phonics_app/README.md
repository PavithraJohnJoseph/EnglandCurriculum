# Year 1 Phonics Screening Practice App

A comprehensive SaaS Django application for UK KS1 phonics screening practice with subscription-based access control.

## Features

- User authentication and registration
- Subscription-based access to phonics practice papers (2012-2025)
- Audio pronunciation support for premium users
- Progress tracking and statistics
- Responsive design for mobile and desktop
- Password reset functionality
- Stripe payment integration
- Admin panel for content management

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL (production) / SQLite (development)
- **Frontend**: HTML5, CSS3, JavaScript
- **Payments**: Stripe
- **Email**: SMTP (Gmail/SendGrid)
- **Deployment**: Docker, Gunicorn, Nginx
- **Monitoring**: Sentry, Loguru

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional, SQLite works for development)
- Stripe account for payments

### Installation

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd phonics-app
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Database setup:**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py setup_initial_data  # Custom command to load plans
   ```

4. **Run development server:**
   ```bash
   python manage.py runserver
   ```

## Deployment

### Docker Deployment
```bash
docker-compose up -d
```

### Manual Deployment
```bash
# Collect static files
python manage.py collectstatic

# Use gunicorn for production
gunicorn phonics_app.wsgi:application --bind 0.0.0.0:8000
```

## Configuration

### Environment Variables
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Django secret key
- `DATABASE_URL`: PostgreSQL connection string
- `STRIPE_PUBLIC_KEY`: Stripe publishable key
- `STRIPE_SECRET_KEY`: Stripe secret key
- `EMAIL_HOST`: SMTP server
- `ALLOWED_HOSTS`: Comma-separated list of allowed domains

## API Documentation

### Authentication Endpoints
- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration
- `POST /api/auth/logout/` - User logout

### Subscription Endpoints
- `GET /api/plans/` - List available plans
- `POST /api/subscribe/` - Create subscription
- `GET /api/progress/` - User progress statistics

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
# Linting
flake8 core/
black core/

# Type checking
mypy core/
```

### Database Management
```bash
# Create migration
python manage.py makemigrations

# Run migrations
python manage.py migrate

# Backup database
python manage.py dumpdata > backup.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@phonicsapp.com or create an issue in the repository.