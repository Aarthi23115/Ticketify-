"""
Load fictional demo data so Ticketify can be tried without a real database.

    python manage.py seed_demo

Creates (or refreshes) categories, two demo accounts and a set of published
events whose dates are always in the future relative to the day you run it.
Safe to run more than once. No real personal data is used.

Demo account password: taken from the DEMO_PASSWORD environment variable,
otherwise a random one is generated and printed once.
"""
import os
import secrets
from datetime import time, timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify

from events.models import Category, Event


CATEGORIES = [
    ('Music', '🎵', 'Concerts, live gigs and music festivals'),
    ('Sports', '🏏', 'Matches, tournaments and screenings'),
    ('Technology', '💻', 'Tech talks, meetups and hackathons'),
    ('Business', '💼', 'Conferences and networking events'),
    ('Arts', '🎨', 'Exhibitions, dance and theatre'),
    ('Food', '🍽️', 'Food festivals and cooking classes'),
    ('Comedy', '😂', 'Stand-up and improv shows'),
    ('Education', '📚', 'Workshops and learning sessions'),
]

# (title, category, event_type, venue, city, days_from_today, start, price, tickets, featured, image)
EVENTS = [
    ('Python for Beginners Workshop', 'Education', 'workshop', 'T-Hub', 'Hyderabad', 7, time(10, 0), '299.00', 60, True, 'python.jpg'),
    ('GenAI Builders Meetup', 'Technology', 'conference', 'HITEC City Convention Hall', 'Hyderabad', 12, time(17, 30), '0.00', 150, True, 'AI.webp'),
    ('Web Development Bootcamp', 'Technology', 'workshop', 'Innovation Centre', 'Bengaluru', 20, time(9, 30), '499.00', 80, False, 'web.webp'),
    ('Startup Networking Evening', 'Business', 'conference', 'Business Lounge, Banjara Hills', 'Hyderabad', 15, time(18, 0), '199.00', 120, False, 'business.webp'),
    ('Electronic Night Live', 'Music', 'concert', 'Open Air Arena', 'Hyderabad', 25, time(19, 0), '999.00', 400, True, 'edm.jpeg'),
    ('Telugu Stand-up Comedy Night', 'Comedy', 'other', 'Laugh Club', 'Hyderabad', 9, time(20, 0), '349.00', 100, True, 'telugu_comedy.jpg'),
    ('Bharatanatyam Evening', 'Arts', 'other', 'Ravindra Bharathi', 'Hyderabad', 30, time(18, 30), '150.00', 200, False, 'bharatanatyam.webp'),
    ('Contemporary Art Exhibition', 'Arts', 'other', 'State Art Gallery', 'Hyderabad', 18, time(11, 0), '0.00', 300, False, 'art_exhibition.jpeg'),
    ('Global Street Food Festival', 'Food', 'other', 'People\'s Plaza', 'Hyderabad', 22, time(16, 0), '99.00', 500, True, 'global_food.webp'),
    ('Chef\'s Table Cooking Class', 'Food', 'workshop', 'Culinary Studio', 'Bengaluru', 14, time(15, 0), '799.00', 25, False, 'chef.jpg'),
    ('Five-a-side Football Cup', 'Sports', 'sports', 'City Sports Complex', 'Hyderabad', 35, time(7, 0), '250.00', 160, False, 'footboll.webp'),
    ('Photography Walk', 'Arts', 'workshop', 'Charminar Heritage Area', 'Hyderabad', 10, time(6, 30), '199.00', 30, False, 'photo.webp'),
]

DEMO_USERS = [
    # username, first, last, is_organizer
    ('demo_organizer', 'Demo', 'Organizer', True),
    ('demo_user', 'Demo', 'Attendee', False),
]


class Command(BaseCommand):
    help = 'Create fictional demo categories, accounts and upcoming events.'

    @transaction.atomic
    def handle(self, *args, **options):
        password = os.environ.get('DEMO_PASSWORD') or secrets.token_urlsafe(9)
        generated = not os.environ.get('DEMO_PASSWORD')

        users = {}
        for username, first, last, is_organizer in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={'first_name': first, 'last_name': last, 'email': f'{username}@example.com'},
            )
            user.set_password(password)
            user.save()
            user.profile.is_organizer = is_organizer
            user.profile.save()
            users[username] = user

        categories = {}
        for name, icon, description in CATEGORIES:
            category, _ = Category.objects.get_or_create(
                name=name, defaults={'icon': icon, 'description': description}
            )
            categories[name] = category

        today = timezone.localdate()
        media_dir = settings.MEDIA_ROOT / 'events'
        for (title, category, event_type, venue, city, days, start, price,
             tickets, featured, image) in EVENTS:
            image_path = f'events/{image}' if (media_dir / image).exists() else ''
            Event.objects.update_or_create(
                slug=slugify(title),
                defaults={
                    'title': title,
                    'description': f'{title} in {city}. This is fictional demo data for the Ticketify portfolio demo.',
                    'category': categories[category],
                    'organizer': users['demo_organizer'],
                    'event_type': event_type,
                    'venue': venue,
                    'address': f'{venue}, {city}',
                    'city': city,
                    'event_date': today + timedelta(days=days),
                    'start_time': start,
                    'price': Decimal(price),
                    'total_tickets': tickets,
                    'available_tickets': tickets,
                    'status': 'published',
                    'is_featured': featured,
                    'image': image_path,
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready: {len(CATEGORIES)} categories, {len(EVENTS)} upcoming events, '
            f'accounts: {", ".join(users)}'
        ))
        if generated:
            self.stdout.write(f'Demo account password (shown once): {password}')
            self.stdout.write('Set DEMO_PASSWORD to choose your own.')
