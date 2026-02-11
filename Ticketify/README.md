# Ticketify - Event Ticketing System

A modern, secure, and user-friendly Django-based event ticketing platform with QR code verification.

## Features

### For Event Attendees
- **Browse Events**: Search and filter events by category, date, price, and location
- **Secure Booking**: Book tickets online with instant confirmation
- **QR Code Tickets**: Receive unique QR code tickets for secure entry
- **Account Management**: View bookings, tickets, and event history
- **Reviews & Ratings**: Share experiences and rate attended events

### For Event Organizers
- **Event Management**: Create, edit, and manage events effortlessly
- **Real-Time Analytics**: Monitor ticket sales, revenue, and attendance
- **QR Code Validation**: Scan and validate tickets at event entrance
- **Booking Insights**: View detailed booking information and attendee lists
- **Capacity Control**: Set and manage event capacity automatically

### Security Features
- **QR Code Verification**: Prevents duplicate and fake tickets
- **Unique Ticket IDs**: Each ticket has a unique identifier
- **Single-Use Validation**: Tickets can only be validated once
- **Secure Authentication**: User authentication with Django's built-in security

### Technical Features
- **Responsive Design**: Mobile-friendly UI with Bootstrap 5
- **Clean Architecture**: Follows Django best practices
- **Scalable Database**: SQLite for development, easily upgradable to PostgreSQL
- **Real-Time Updates**: Automatic ticket generation and inventory management

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Installation

### 1. Clone or Download the Project

```bash
cd Ticketify
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Apply Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Load Sample Data (Optional)

```bash
python manage.py shell < setup_data.py
```

Or manually create categories and events via the admin panel.

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Usage Guide

### For Regular Users

1. **Register**: Click "Sign Up" and create an account
2. **Browse Events**: Explore events on the homepage or events page
3. **Book Tickets**: Select an event, click "Book Now", and complete the booking
4. **View Tickets**: Access your tickets from "My Tickets" with QR codes
5. **Attend Event**: Show your QR code ticket at the event entrance

### For Event Organizers

1. **Register as Organizer**: Check "Register as Event Organizer" during signup
2. **Create Event**: Access "Organizer Dashboard" → "Create New Event"
3. **Fill Event Details**: Add title, description, venue, date, pricing, capacity
4. **Publish Event**: Set status to "Published" to make it visible
5. **Monitor Sales**: View bookings, revenue, and analytics in dashboard
6. **Validate Tickets**: Use "Validate Tickets" to scan QR codes at entrance

### Admin Panel

Access the admin panel at `http://127.0.0.1:8000/admin/`

- Manage users, events, bookings, tickets, and categories
- View comprehensive data and statistics
- Moderate content and handle issues

## Project Structure

```
Ticketify/
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
├── ticketify_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── events/
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── forms.py           # Form definitions
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin configuration
│   └── signals.py         # Signal handlers
├── templates/
│   ├── base.html
│   └── events/            # Event-related templates
├── static/                # Static files (CSS, JS)
└── media/                 # User uploads (images, QR codes)
```

## Key Models

- **UserProfile**: Extended user information and organizer status
- **Category**: Event categories for organization
- **Event**: Event details, pricing, and capacity
- **Booking**: Ticket purchase orders
- **Ticket**: Individual tickets with QR codes
- **Review**: Event ratings and reviews

## Technologies Used

- **Backend**: Django 4.2
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (development), PostgreSQL-ready
- **QR Codes**: qrcode library with PIL
- **Icons**: Bootstrap Icons
- **Image Processing**: Pillow

## Configuration

### Email Settings (Optional)

Update `settings.py` for email notifications:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Production Deployment

For production deployment:

1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS` with your domain
3. Change `SECRET_KEY` to a secure value
4. Use PostgreSQL instead of SQLite
5. Configure static file serving with WhiteNoise or CDN
6. Set up proper email backend
7. Use environment variables for sensitive data

## Security Considerations

- QR codes contain unique verification codes
- Tickets can only be validated once
- User authentication required for booking
- CSRF protection enabled
- SQL injection prevention with Django ORM
- XSS protection with template auto-escaping

## Troubleshooting

### QR Code Images Not Generating

Ensure Pillow is installed:
```bash
pip install Pillow
```

### Static Files Not Loading

Run:
```bash
python manage.py collectstatic
```

### Database Errors

Reset database:
```bash
python manage.py flush
python manage.py migrate
```

## Support

For issues or questions:
- Email: support@ticketify.com
- Documentation: Check this README
- Admin Panel: Use built-in Django admin

## License

This project is proprietary software developed for event ticketing purposes.

## Credits

Developed with ❤️ using Django and Bootstrap

---

**Version**: 1.0.0  
**Last Updated**: February 2026
"# Ticketify-" 
