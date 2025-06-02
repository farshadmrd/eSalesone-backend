# eSalesOne Backend API

A comprehensive Django REST API backend for the eSalesOne e-commerce platform. This system manages user profiles, services, transactions, and includes automated email notifications for transaction processing.

## 🚀 Features

- **User Profile Management**: Create and manage user profiles with personal and professional details
- **Contact Information**: Store and manage contact details for users
- **Service Management**: Catalog of services with different types and pricing
- **Transaction Processing**: Complete transaction workflow with validation and email notifications
- **Shopping Basket**: Manage service collections before purchase
- **Email Notifications**: Automated email system for transaction status updates
- **File Upload Support**: Handle profile pictures, logos, and other media files
- **Admin Interface**: Django admin panel for easy data management
- **RESTful API**: Well-structured API endpoints with proper HTTP methods

## 🏗️ Project Structure

```
eSalesone-backend/
├── core/                   # User profiles and contact management
│   ├── models.py          # Profile and Contact models
│   ├── views.py           # API viewsets
│   ├── serializers.py     # Data serialization
│   └── admin.py           # Admin configuration
├── service/               # Service and type management
│   ├── models.py          # Service and Type models
│   ├── views.py           # Service API views
│   └── serializers.py     # Service serialization
├── transaction/           # Transaction processing
│   ├── models.py          # Transaction and Basket models
│   ├── views.py           # Transaction API views
│   ├── email_service.py   # Email notification service
├── templates/             # Email templates
│   └── emails/            # HTML and text email templates
├── media/                 # User uploaded files
├── esale_project/         # Django project settings
│   ├── settings.py        # Project configuration
│   └── urls.py            # URL routing
└── manage.py              # Django management script
```

## 🛠️ Technology Stack

- **Backend Framework**: Django 5.2.1
- **API Framework**: Django REST Framework 3.15.2
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Image Processing**: Pillow
- **Environment Management**: python-dotenv
- **Email Service**: SMTP (configurable)

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- Virtual environment (recommended)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
cd eSalesone-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```env
# Email Configuration (Optional - defaults provided)
EMAIL_HOST=sandbox.smtp.mailtrap.io
EMAIL_PORT=2525
EMAIL_USERNAME=your_email_username
EMAIL_PASSWORD=your_email_password

# Security (Change in production)
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (Optional - SQLite used by default)
# DATABASE_URL=postgresql://user:password@localhost:5432/esalesone
```

### 3. Database Setup

```bash
# Apply database migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser

# Load initial data (optional)
# python manage.py loaddata initial_data.json
```

### 4. Run the Development Server

```bash
# Start the development server
python manage.py runserver

# Server will be available at: http://127.0.0.1:8000/
```

## 📚 API Documentation

### Base URL
```
http://127.0.0.1:8000/api/
```

### Core Endpoints

#### Profiles
- `GET /api/profiles/` - List all profiles
- `POST /api/profiles/` - Create new profile
- `GET /api/profiles/{name}/` - Get profile by name
- `PUT /api/profiles/{name}/` - Update profile
- `DELETE /api/profiles/{name}/` - Delete profile

#### Contacts
- `GET /api/contacts/` - List all contacts
- `POST /api/contacts/` - Create new contact
- `GET /api/contacts/{id}/` - Get contact details
- `PUT /api/contacts/{id}/` - Update contact
- `DELETE /api/contacts/{id}/` - Delete contact

#### Services
- `GET /api/services/` - List all services
- `GET /api/services/?title={title}` - Get service types by title
- `GET /api/types/` - List all service types

#### Transactions
- `GET /api/transactions/` - List all transactions
- `POST /api/transactions/` - Create new transaction
- `GET /api/transactions/{id}/` - Get transaction details
- `PUT /api/transactions/{id}/` - Update transaction status

#### Baskets
- `GET /api/baskets/` - List all baskets
- `POST /api/baskets/` - Create new basket
- `GET /api/baskets/{id}/` - Get basket details

### Authentication
- `GET /api-auth/login/` - Login interface
- `GET /api-auth/logout/` - Logout interface

### Admin Interface
- `GET /admin/` - Django admin panel

## 🧪 Testing

### Transaction Testing
The system includes special test card numbers for development:

- **Card Number `1`**: ✅ Approved transaction
- **Card Number `2`**: ❌ Declined transaction  
- **Card Number `3`**: ⚠️ Gateway failure

### Email Testing
Test email configuration:
```bash
python test_email.py
```

### Run Unit Tests
```bash
python manage.py test
```

## 📁 File Uploads

The system supports file uploads for:
- Profile pictures (`/media/profile_pictures/`)
- Secondary pictures (`/media/secondary_pictures/`)
- Service logos (`/media/logos/`)

## 📧 Email System

### Email Templates
- Transaction approved: `templates/emails/transaction_approved.html`
- Transaction failed: `templates/emails/transaction_failed.html`

### Email Configuration
Configure email settings in `.env` file or `settings.py`. The system supports:
- SMTP email backend
- Console email backend (for development)
- Custom email service integration

## 🔧 Configuration

### Key Settings

```python
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media Files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'sandbox.smtp.mailtrap.io'
EMAIL_PORT = 2525
```

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**:
   ```env
   DEBUG=False
   SECRET_KEY=your-production-secret-key
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

2. **Database**: Configure PostgreSQL
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/esalesone_prod
   ```

3. **Static Files**:
   ```bash
   python manage.py collectstatic
   ```

4. **Security**: Update security settings in `settings.py`

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Documentation: [API Docs](http://127.0.0.1:8000/api/)
- Admin Panel: [Admin](http://127.0.0.1:8000/admin/)

## 📊 Project Status

- ✅ Core functionality implemented
- ✅ API endpoints working
- ✅ Email system configured
- ✅ File upload support
- ✅ Admin interface available
- ✅ Transaction validation
- 🔄 Additional features in development

---

**Built with ❤️ using Django and Django REST Framework**