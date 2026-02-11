from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from events.models import Category, Event, Booking, Ticket, UserProfile
from decimal import Decimal


class UserProfileTestCase(TestCase):
    """Test cases for UserProfile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_profile_creation(self):
        """Test that user profile is created automatically"""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_organizer_status(self):
        """Test organizer status functionality"""
        self.assertFalse(self.user.profile.is_organizer)
        self.user.profile.is_organizer = True
        self.user.profile.save()
        self.assertTrue(self.user.profile.is_organizer)


class EventModelTestCase(TestCase):
    """Test cases for Event model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        self.user.profile.is_organizer = True
        self.user.profile.save()
        
        self.category = Category.objects.create(
            name='Music',
            icon='🎵',
            description='Music events'
        )
        
        self.event = Event.objects.create(
            title='Test Concert',
            slug='test-concert',
            description='A test concert event',
            category=self.category,
            organizer=self.user,
            venue='Test Venue',
            address='123 Test St',
            city='Test City',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=30, hours=3),
            price=Decimal('50.00'),
            total_tickets=100,
            status='published'
        )
    
    def test_event_creation(self):
        """Test event is created correctly"""
        self.assertEqual(self.event.title, 'Test Concert')
        self.assertEqual(self.event.available_tickets, 100)
    
    def test_event_is_upcoming(self):
        """Test event is_upcoming property"""
        self.assertTrue(self.event.is_upcoming)
    
    def test_tickets_sold_calculation(self):
        """Test tickets_sold property"""
        self.event.available_tickets = 80
        self.event.save()
        self.assertEqual(self.event.tickets_sold, 20)
    
    def test_sales_percentage(self):
        """Test sales_percentage property"""
        self.event.available_tickets = 75
        self.event.save()
        self.assertEqual(self.event.sales_percentage, 25.0)


class BookingTestCase(TestCase):
    """Test cases for Booking model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        
        self.category = Category.objects.create(name='Music', icon='🎵')
        
        self.event = Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test Description',
            category=self.category,
            organizer=self.organizer,
            venue='Test Venue',
            address='Test Address',
            city='Test City',
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=7, hours=3),
            price=Decimal('25.00'),
            total_tickets=50,
            status='published'
        )
    
    def test_booking_creation(self):
        """Test booking is created with correct details"""
        booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=2,
            email='customer@example.com',
            phone='555-0100',
            status='confirmed'
        )
        
        self.assertIsNotNone(booking.booking_id)
        self.assertEqual(booking.quantity, 2)
        self.assertEqual(booking.total_amount, Decimal('50.00'))
    
    def test_booking_id_generation(self):
        """Test unique booking ID is generated"""
        booking1 = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=1,
            email='test@example.com',
            phone='555-0100',
            status='confirmed'
        )
        
        booking2 = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=1,
            email='test@example.com',
            phone='555-0100',
            status='confirmed'
        )
        
        self.assertNotEqual(booking1.booking_id, booking2.booking_id)


class TicketTestCase(TestCase):
    """Test cases for Ticket model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.organizer = User.objects.create_user(username='organizer', password='testpass123')
        self.category = Category.objects.create(name='Test Category', icon='🎪')
        
        self.event = Event.objects.create(
            title='Test Event',
            slug='test-event',
            description='Test',
            category=self.category,
            organizer=self.organizer,
            venue='Test Venue',
            address='Test Address',
            city='Test City',
            start_date=timezone.now() + timedelta(days=7),
            end_date=timezone.now() + timedelta(days=7, hours=3),
            price=Decimal('10.00'),
            total_tickets=10,
            status='published'
        )
        
        self.booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=1,
            email='test@example.com',
            phone='555-0100',
            status='confirmed'
        )
    
    def test_ticket_creation(self):
        """Test ticket is created with QR code"""
        ticket = Ticket.objects.create(
            booking=self.booking,
            event=self.event,
            user=self.user,
            attendee_name='Test User',
            attendee_email='test@example.com'
        )
        
        self.assertIsNotNone(ticket.ticket_id)
        self.assertIsNotNone(ticket.verification_code)
    
    def test_ticket_validation(self):
        """Test ticket can be marked as used"""
        ticket = Ticket.objects.create(
            booking=self.booking,
            event=self.event,
            user=self.user,
            attendee_name='Test User',
            attendee_email='test@example.com'
        )
        
        self.assertEqual(ticket.status, 'valid')
        ticket.mark_as_used(self.organizer)
        self.assertEqual(ticket.status, 'used')
        self.assertIsNotNone(ticket.validated_at)


class ViewsTestCase(TestCase):
    """Test cases for views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ticketify')
    
    def test_events_list_page(self):
        """Test events list page loads"""
        response = self.client.get(reverse('events_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
    
    def test_register_page(self):
        """Test registration page loads"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
    
    def test_user_login(self):
        """Test user can login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
    
    def test_protected_view_requires_login(self):
        """Test that protected views require authentication"""
        response = self.client.get(reverse('my_bookings'))
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)


class BookingFlowTestCase(TestCase):
    """Test complete booking flow"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='customer',
            email='customer@example.com',
            password='testpass123'
        )
        
        self.organizer = User.objects.create_user(
            username='organizer',
            email='organizer@example.com',
            password='testpass123'
        )
        self.organizer.profile.is_organizer = True
        self.organizer.profile.save()
        
        self.category = Category.objects.create(name='Music', icon='🎵')
        
        self.event = Event.objects.create(
            title='Test Concert',
            slug='test-concert',
            description='A great concert',
            category=self.category,
            organizer=self.organizer,
            venue='Test Arena',
            address='123 Music St',
            city='New York',
            start_date=timezone.now() + timedelta(days=30),
            end_date=timezone.now() + timedelta(days=30, hours=3),
            price=Decimal('75.00'),
            total_tickets=100,
            status='published'
        )
    
    def test_complete_booking_flow(self):
        """Test user can complete a booking"""
        # Login
        self.client.login(username='customer', password='testpass123')
        
        # View event detail
        response = self.client.get(reverse('event_detail', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Go to booking page
        response = self.client.get(reverse('book_ticket', kwargs={'slug': self.event.slug}))
        self.assertEqual(response.status_code, 200)
        
        # Submit booking
        response = self.client.post(reverse('book_ticket', kwargs={'slug': self.event.slug}), {
            'quantity': 2,
            'email': 'customer@example.com',
            'phone': '555-0100'
        })
        
        # Should redirect to confirmation
        self.assertEqual(response.status_code, 302)
        
        # Check booking was created
        booking = Booking.objects.filter(user=self.user, event=self.event).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.quantity, 2)
        self.assertEqual(booking.total_amount, Decimal('150.00'))
        
        # Check tickets were created
        tickets = booking.tickets.all()
        self.assertEqual(tickets.count(), 2)


# Run tests with: python manage.py test
