# Getting Started Guide - Year 1 Phonics App

A production-ready Django application for UK KS1 phonics screening practice.

## 🚀 Quick Start (Development)

### 1. Clone & Setup
```bash
git clone <repo-url>
cd phonics_app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Database Setup
```bash
python manage.py migrate
python manage.py setup_initial_data
python manage.py createsuperuser
```

### 3. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

### 4. Run Tests
```bash
pytest                           # Run all tests
pytest core/tests/test_auth.py   # Run specific test file
pytest --cov=core               # Generate coverage report
```

## 📋 Feature Breakdown

### User Management
- ✅ Registration and authentication
- ✅ Email verification (password reset)
- ✅ Profile customization
- ✅ Session management

### Plans & Subscriptions
- ✅ Freemium model (Bronze = free, Silver/Gold = paid)
- ✅ Year-based access control
- ✅ Audio pronunciation (premium feature)
- ✅ Stripe payment integration

### Practice Features
- ✅ Interactive phonics practice papers
- ✅ Progress tracking
- ✅ Real/pseudo word differentiation
- ✅ Audio pronunciation support
- ✅ Celebration animations on completion

### Admin
- ✅ Django admin panel
- ✅ Plan management
- ✅ User management
- ✅ Payment tracking
- ✅ Content management

## 🏗️ Architecture Overview

```
phonics_app/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Django forms
│   ├── urls.py             # URL routing
│   ├── templates/          # HTML templates
│   ├── static/             # CSS, JS, images
│   ├── tests/              # Test suite
│   └── management/         # Custom commands
├── phonics_app/            # Project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py             # WSGI entry point
├── media/                  # User uploads
├── staticfiles/            # Collected static (production)
├── Dockerfile              # Docker image definition
├── docker-compose.yml      # Docker Compose setup
└── requirements.txt        # Python dependencies
```

## 🔧 Configuration

### Environment Variables
See `.env.example` for all available options:

```bash
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost/db
ALLOWED_HOSTS=localhost,yourdomain.com
STRIPE_PUBLIC_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
```

### Database
Development: SQLite (default)
Production: PostgreSQL (recommended)

Switch via `DATABASE_URL` environment variable.

## 📚 API Reference

### Authentication
- `POST /signup/` - Register new user
- `POST /login/` - User login
- `GET /logout/` - User logout
- `POST /password-reset/` - Password reset

### User Pages
- `GET /dashboard/` - User dashboard
- `GET /plans/` - Plan selection
- `GET /years/` - Year selection
- `GET /progress/` - Progress report

### Practice
- `GET /paper/<id>/page/<num>/` - Practice page
- `POST /paper/<id>/page/<num>/` - Submit response

## 🧪 Testing

### Test Files
- `test_auth.py` - Authentication tests
- `test_plans.py` - Plan/subscription tests
- `test_practice.py` - Practice feature tests

### Run Tests
```bash
# All tests with coverage
pytest --cov=core --cov-report=html

# Specific test
pytest core/tests/test_auth.py::TestUserModel::test_user_creation -v

# Watch mode
pytest-watch
```

## 📦 Deployment

### Docker (Recommended)
```bash
docker-compose --env-file .env.production up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment guide.

### Manual Deployment
```bash
# Install production server
pip install gunicorn

# Collect static files
python manage.py collectstatic

# Run with gunicorn
gunicorn --bind 0.0.0.0:8000 phonics_app.wsgi:application
```

## 🔐 Security

### Production Checklist
- [ ] `DEBUG=False`
- [ ] Unique `SECRET_KEY`
- [ ] HTTPS enabled
- [ ] Database backups scheduled
- [ ] SSL certificate installed
- [ ] Security headers configured
- [ ] CORS properly restricted
- [ ] Admin panel protected

## 📊 Database Schema

### Models
- **User** - Extends Django User with plan and subscription info
- **Plan** - Subscription tiers (Bronze/Silver/Gold)
- **Subscription** - User subscription tracking
- **PaperYear** - Phonics practice papers by year
- **PaperPage** - Individual pages within papers
- **Word** - Words to practice on each page
- **UserProgress** - Track user progress per paper

## 🐛 Troubleshooting

### Common Issues

**Database connection error**
```bash
# Check DATABASE_URL
python manage.py dbshell

# For PostgreSQL, ensure postgres is running
sudo service postgresql start
```

**Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**Import errors**
```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**Tests failing**
```bash
# Run with verbose output
pytest -vv --tb=long
pytest --lf  # Run last failed tests
```

## 📞 Support

For issues or questions:
1. Check logs: `python manage.py check`
2. Review tests: `pytest -v`
3. Check docs: See [DEPLOYMENT.md](DEPLOYMENT.md)

## 📝 Development Workflow

1. **Create feature branch**: `git checkout -b feature/my-feature`
2. **Make changes** and test: `pytest`
3. **Run linting**: `black core/` and `flake8 core/`
4. **Commit and push**: `git push origin feature/my-feature`
5. **Create pull request**

## 🎯 Next Steps

1. **Customize content**: Add phonics papers to `/media/paper_images/`
2. **Configure Stripe**: Add real payment keys
3. **Setup email**: Configure SMTP for password resets
4. **Deploy**: Follow [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Monitor**: Setup logging and error tracking

## 📄 License

MIT License - See LICENSE file for details

---

**Happy phonics teaching! 📚✨**
