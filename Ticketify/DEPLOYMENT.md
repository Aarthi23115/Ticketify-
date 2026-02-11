# Ticketify - Production Deployment Guide

## Overview
This guide covers deploying Ticketify to production environments.

---

## Pre-Deployment Checklist

### 1. Security Configuration

**Update settings.py**:

```python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-production-secret-key')

# Update allowed hosts
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'your-ip-address']

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### 2. Database Configuration

**PostgreSQL (Recommended)**:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'ticketify_db'),
        'USER': os.environ.get('DB_USER', 'ticketify_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Install PostgreSQL adapter:
```bash
pip install psycopg2-binary
```

### 3. Email Configuration

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@ticketify.com')
```

---

## Deployment Options

### Option 1: Deploy to Heroku

1. **Install Heroku CLI**
2. **Create Procfile**:
```
web: gunicorn ticketify_project.wsgi
```

3. **Create runtime.txt**:
```
python-3.11.0
```

4. **Update requirements.txt**:
```
gunicorn
dj-database-url
whitenoise
psycopg2-binary
```

5. **Deploy**:
```bash
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### Option 2: Deploy to DigitalOcean/AWS

**1. Server Setup** (Ubuntu):
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx postgresql postgresql-contrib

# Create database
sudo -u postgres createdb ticketify_db
sudo -u postgres createuser ticketify_user
sudo -u postgres psql
ALTER USER ticketify_user WITH PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE ticketify_db TO ticketify_user;
```

**2. Deploy Application**:
```bash
# Clone repository
git clone your-repo-url /var/www/ticketify
cd /var/www/ticketify

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Collect static files
python manage.py collectstatic --noinput

# Migrate database
python manage.py migrate
```

**3. Configure Gunicorn**:

Create `/etc/systemd/system/ticketify.service`:
```ini
[Unit]
Description=Ticketify Gunicorn Service
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/ticketify
Environment="PATH=/var/www/ticketify/venv/bin"
ExecStart=/var/www/ticketify/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/var/www/ticketify/ticketify.sock \
    ticketify_project.wsgi:application

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl start ticketify
sudo systemctl enable ticketify
```

**4. Configure Nginx**:

Create `/etc/nginx/sites-available/ticketify`:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/ticketify;
    }
    
    location /media/ {
        root /var/www/ticketify;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/ticketify/ticketify.sock;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ticketify /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

**5. Setup SSL with Let's Encrypt**:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### Option 3: Deploy to PythonAnywhere

1. Upload files via web interface
2. Set up virtual environment
3. Configure WSGI file
4. Set environment variables
5. Collect static files
6. Migrate database

---

## Environment Variables

Create `.env` file (never commit this):
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
DB_NAME=ticketify_db
DB_USER=ticketify_user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Install python-decouple:
```bash
pip install python-decouple
```

Update settings.py:
```python
from decouple import config

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=lambda v: [s.strip() for s in v.split(',')])
```

---

## Static Files Configuration

**Using WhiteNoise** (recommended):

1. Install WhiteNoise:
```bash
pip install whitenoise
```

2. Update settings.py:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

3. Collect static files:
```bash
python manage.py collectstatic
```

---

## Monitoring & Logging

### 1. Application Logs

Update settings.py:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/ticketify/error.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

### 2. Performance Monitoring

Consider using:
- **Sentry** for error tracking
- **New Relic** for performance monitoring
- **Datadog** for comprehensive monitoring

---

## Backup Strategy

### Database Backup

**PostgreSQL**:
```bash
# Backup
pg_dump -U ticketify_user ticketify_db > backup.sql

# Restore
psql -U ticketify_user ticketify_db < backup.sql
```

**Automated Backup Script**:
```bash
#!/bin/bash
BACKUP_DIR="/backups/ticketify"
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U ticketify_user ticketify_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz
find $BACKUP_DIR -mtime +30 -delete  # Delete backups older than 30 days
```

Add to cron:
```bash
0 2 * * * /path/to/backup-script.sh
```

### Media Files Backup

```bash
tar -czf media_backup_$(date +%Y%m%d).tar.gz media/
```

---

## Performance Optimization

### 1. Database Optimization

```python
# Add database indexes
class Event(models.Model):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'start_date']),
            models.Index(fields=['slug']),
        ]
```

### 2. Caching

Install Redis:
```bash
pip install django-redis
```

Update settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

### 3. Image Optimization

Install Pillow-SIMD (faster):
```bash
pip uninstall pillow
pip install pillow-simd
```

---

## Security Hardening

### 1. Firewall Configuration

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### 2. Regular Updates

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Update Python packages
pip install --upgrade -r requirements.txt
```

### 3. Fail2ban (Prevent brute force)

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use Nginx or AWS ELB
2. **Database Replication**: Master-slave PostgreSQL
3. **CDN**: CloudFlare or AWS CloudFront for static files
4. **Message Queue**: Celery with Redis for background tasks

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize database queries
3. Enable caching
4. Use connection pooling

---

## Post-Deployment

### 1. Health Checks

Create monitoring endpoint:
```python
def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### 2. Documentation

- Document deployment process
- Keep credentials secure
- Maintain server access list
- Document backup procedures

### 3. Testing

```bash
# Run tests
python manage.py test

# Check for security issues
python manage.py check --deploy
```

---

## Maintenance

### Regular Tasks

- **Daily**: Monitor logs, check backups
- **Weekly**: Review performance metrics
- **Monthly**: Security updates, database optimization
- **Quarterly**: Full system review, disaster recovery test

---

## Rollback Procedure

If deployment fails:

1. Stop application
2. Restore database from backup
3. Restore previous code version
4. Restart services
5. Test functionality
6. Investigate issues

---

## Support Resources

- Django Documentation: https://docs.djangoproject.com/
- PostgreSQL Docs: https://www.postgresql.org/docs/
- Nginx Docs: http://nginx.org/en/docs/
- Let's Encrypt: https://letsencrypt.org/

---

**Production Checklist**:
- [ ] DEBUG = False
- [ ] SECRET_KEY changed
- [ ] ALLOWED_HOSTS configured
- [ ] Database configured (PostgreSQL)
- [ ] Static files collected
- [ ] Media files configured
- [ ] Email configured
- [ ] SSL certificate installed
- [ ] Backups automated
- [ ] Monitoring set up
- [ ] Firewall configured
- [ ] Security headers enabled
- [ ] Error logging configured

---

**Need Help?**
Contact: devops@ticketify.com
