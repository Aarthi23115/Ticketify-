import json
from urllib.parse import parse_qs, urlparse
from django.test import TestCase, Client
from django.test import override_settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from events.models import Category, Event, Booking, Ticket, UserProfile, TicketScanLog
from decimal import Decimal
from events.services.qr_service import make_share_token, make_token, verify_share_token, verify_token
from socket import AF_INET, SOCK_STREAM
from unittest.mock import patch


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
            event_date=(timezone.now() + timedelta(days=30)).date(),
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
            event_date=(timezone.now() + timedelta(days=7)).date(),
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
            event_date=(timezone.now() + timedelta(days=7)).date(),
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
        self.assertNotContains(response, 'Register as Event Organizer')

    def test_public_registration_cannot_grant_organizer_or_owner_access(self):
        response = self.client.post(reverse('register'), {
            'username': 'new-customer',
            'first_name': 'New',
            'last_name': 'Customer',
            'email': 'new-customer@example.com',
            'password1': 'a-strong-pass-123',
            'password2': 'a-strong-pass-123',
            'is_organizer': 'on',
        })
        self.assertEqual(response.status_code, 302)
        customer = User.objects.get(username='new-customer')
        self.assertFalse(customer.profile.is_organizer)
        self.assertFalse(customer.is_staff)
        self.assertFalse(customer.is_superuser)
        self.assertEqual(self.client.get(reverse('owner_dashboard')).status_code, 403)
    
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
            event_date=(timezone.now() + timedelta(days=30)).date(),
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


@override_settings(QR_REFRESH_INTERVAL=30, QR_LEEWAY_SECONDS=60)
class QRValidationAPITestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='qr-attendee', password='testpass123')
        self.organizer = User.objects.create_user(username='qr-organizer', password='testpass123')
        self.category = Category.objects.create(name='QR Test', icon='🎟️')
        self.event = Event.objects.create(
            title='QR Test Event',
            slug='qr-test-event',
            description='Test QR validation',
            category=self.category,
            organizer=self.organizer,
            venue='Test Venue',
            address='Test Address',
            city='Test City',
            event_date=timezone.now().date() + timedelta(days=7),
            price=Decimal('10.00'),
            total_tickets=10,
            status='published',
        )
        self.booking = Booking.objects.create(
            user=self.user,
            event=self.event,
            quantity=1,
            email='qr-attendee@example.com',
            phone='555-0100',
            status='confirmed',
        )
        self.ticket = Ticket.objects.create(
            booking=self.booking,
            event=self.event,
            user=self.user,
            attendee_name='QR Attendee',
            attendee_email='qr-attendee@example.com',
            qr_code='qrcodes/qr-test.png',
        )
        self.validation_url = reverse('api_qr_validate')
        self.client.force_login(self.organizer)

    def post_token(self, token):
        return self.client.post(
            self.validation_url,
            data=json.dumps({'token': token}),
            content_type='application/json',
        )

    def test_owner_dashboard_is_superuser_only(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('owner_dashboard')).status_code, 403)

        self.client.force_login(self.organizer)
        self.assertEqual(self.client.get(reverse('owner_dashboard')).status_code, 403)

        owner = User.objects.create_superuser(
            username='site-owner',
            email='owner@example.com',
            password='secure-test-pass',
        )
        self.client.force_login(owner)
        response = self.client.get(reverse('owner_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Owner Dashboard')
        self.assertContains(response, 'Live ticket scan history')

    def test_event_scanner_is_separate_and_scoped_to_event_owner(self):
        self.client.force_login(self.organizer)
        response = self.client.get(reverse('event_scanner'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.title)
        self.assertNotContains(response, 'Owner Dashboard')

        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('event_scanner')).status_code, 403)

    def test_superuser_can_open_scanner_and_validate_any_event(self):
        owner = User.objects.create_superuser(
            username='scanner-owner',
            email='scanner-owner@example.com',
            password='secure-test-pass',
        )
        self.client.force_login(owner)

        scanner_page = self.client.get(reverse('event_scanner'))
        self.assertEqual(scanner_page.status_code, 200)
        self.assertContains(scanner_page, self.event.title)
        self.assertEqual(
            self.client.get(
                reverse('validate_ticket', kwargs={'slug': self.event.slug})
            ).status_code,
            200,
        )

        response = self.post_token(make_token(self.ticket))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['detail'], 'VALID')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.validated_by, owner)

    def test_other_authenticated_device_observes_used_state_and_scan_history(self):
        token = make_token(self.ticket)
        first_device = self.client
        self.assertEqual(first_device.post(
            self.validation_url,
            data=json.dumps({'token': token}),
            content_type='application/json',
        ).status_code, 200)

        second_device = Client()
        second_device.force_login(self.organizer)
        second_response = second_device.post(
            self.validation_url,
            data=json.dumps({'token': token}),
            content_type='application/json',
        )
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(second_response.json()['detail'], 'ALREADY USED')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'used')

        logs = TicketScanLog.objects.filter(ticket=self.ticket).order_by('success')
        self.assertEqual(logs.count(), 2)
        self.assertEqual(
            set(logs.values_list('scanner__username', flat=True)),
            {self.organizer.username},
        )

    def test_owner_scan_history_polling_endpoint_is_protected_and_live(self):
        token = make_token(self.ticket)
        self.post_token(token)

        self.assertEqual(
            self.client.get(reverse('owner_scan_history')).status_code,
            403,
        )
        owner = User.objects.create_superuser(
            username='history-owner',
            email='history@example.com',
            password='secure-test-pass',
        )
        self.client.force_login(owner)
        response = self.client.get(reverse('owner_scan_history'))
        self.assertEqual(response.status_code, 200)
        scan = response.json()['scans'][0]
        self.assertEqual(scan['ticket_id'], self.ticket.ticket_id)
        self.assertEqual(scan['event'], self.event.title)
        self.assertEqual(scan['ticket_status'], 'used')
        self.assertEqual(scan['scanner'], self.organizer.username)
        self.assertEqual(
            response.json()['statistics']['used_tickets'],
            self.booking.tickets.count(),
        )

    def test_expired_token_is_rejected_even_with_configured_leeway(self):
        old_timestamp = int(timezone.now().timestamp()) - 60
        token = make_token(self.ticket, now_ts=old_timestamp)

        response = self.post_token(token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'QR Code Expired. Please Scan the Latest QR Code.')
        self.assertEqual(response.json()['ticket']['booking_id'], self.booking.booking_id)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'valid')

    def test_valid_token_marks_ticket_used_and_rejects_reuse(self):
        token = make_token(self.ticket)

        response = self.post_token(token)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['detail'], 'VALID')
        self.assertEqual(response.json()['ticket']['booking_id'], self.booking.booking_id)
        self.assertEqual(response.json()['ticket']['tickets_booked'], self.booking.quantity)
        self.assertEqual(response.json()['ticket']['tickets_available'], self.event.available_tickets)
        self.assertEqual(response.json()['ticket']['ticket_status'], 'used')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'used')
        self.assertEqual(self.ticket.qr_status, 'USED')

        second_response = self.post_token(token)
        self.assertEqual(second_response.status_code, 400)
        self.assertEqual(second_response.json()['detail'], 'ALREADY USED')
        self.assertEqual(second_response.json()['ticket']['booking_id'], self.booking.booking_id)

        refreshed_token = make_token(
            self.ticket,
            now_ts=int(timezone.now().timestamp()) + 30,
        )
        refreshed_response = self.post_token(refreshed_token)
        self.assertEqual(refreshed_response.status_code, 400)
        self.assertEqual(refreshed_response.json()['detail'], 'ALREADY USED')

    @override_settings(DEBUG=True, QR_PUBLIC_BASE_URL='')
    def test_qr_generation_encodes_a_mobile_reachable_validation_url(self):
        self.client.force_login(self.user)
        lan_address = (AF_INET, SOCK_STREAM, 6, '', ('192.168.1.6', 0))
        with patch('events.api_views.socket.getaddrinfo', return_value=[lan_address]):
            response = self.client.get(
                reverse('api_qr_generate', kwargs={'ticket_id': self.ticket.ticket_id}),
                HTTP_HOST='localhost:8000',
            )

        self.assertEqual(response.status_code, 200)
        scan_url = response.json()['scan_url']
        self.assertEqual(urlparse(scan_url).netloc, '192.168.1.6:8000')
        self.assertEqual(urlparse(scan_url).path, reverse('qr_scan'))
        self.assertEqual(parse_qs(urlparse(scan_url).query)['token'][0], response.json()['token'])

    def test_used_ticket_with_expired_qr_reports_used(self):
        self.ticket.mark_as_used(self.organizer)
        old_timestamp = int(timezone.now().timestamp()) - 60
        token = make_token(self.ticket, now_ts=old_timestamp)

        response = self.post_token(token)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['detail'], 'ALREADY USED')
        self.assertEqual(response.json()['ticket']['booking_id'], self.booking.booking_id)

    def test_booking_confirmation_uses_rotating_qr_not_legacy_qr_image(self):
        self.booking.quantity = 3
        self.booking.save(update_fields=['quantity'])
        Ticket.objects.create(
            booking=self.booking,
            event=self.event,
            user=self.user,
            attendee_name='Second QR Attendee',
            attendee_email='qr-attendee@example.com',
            qr_code='qrcodes/qr-test-2.png',
        )
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('booking_confirmation', kwargs={'booking_id': self.booking.booking_id})
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="ticket-live-qr img-fluid"', count=1)
        self.assertContains(response, '3 tickets in this booking')
        self.assertContains(response, 'QR screenshots expire')

    def test_one_booking_qr_checks_in_all_tickets_and_rejects_refreshed_qr(self):
        self.booking.quantity = 3
        self.booking.save(update_fields=['quantity'])
        extra_ticket = Ticket.objects.create(
            booking=self.booking,
            event=self.event,
            user=self.user,
            attendee_name='QR Attendee 2',
            attendee_email='qr-attendee@example.com',
            qr_code='qrcodes/qr-test-2.png',
        )

        self.client.force_login(self.user)
        generated = self.client.get(
            reverse('api_qr_generate', kwargs={'ticket_id': extra_ticket.ticket_id})
        )
        self.assertEqual(generated.status_code, 200)
        payload, _ = verify_token(generated.json()['token'])
        canonical_ticket_id = self.booking.tickets.order_by('pk').first().ticket_id
        self.assertEqual(payload['ticket_id'], canonical_ticket_id)

        self.client.force_login(self.organizer)
        response = self.post_token(generated.json()['token'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['ticket']['tickets_booked'], 3)
        self.assertEqual(
            list(self.booking.tickets.order_by('pk').values_list('status', flat=True)),
            ['used', 'used', 'used'],
        )

        refreshed_payload = make_token(self.ticket, now_ts=int(timezone.now().timestamp()) + 30)
        refreshed_response = self.post_token(refreshed_payload)
        self.assertEqual(refreshed_response.status_code, 400)
        self.assertEqual(refreshed_response.json()['detail'], 'ALREADY USED')

    def test_signed_share_link_opens_live_booking_qr_without_owner_login(self):
        self.booking.quantity = 3
        self.booking.save(update_fields=['quantity'])
        canonical_ticket = self.booking.tickets.order_by('pk').first()
        share_token = make_share_token(canonical_ticket.ticket_id)
        self.assertEqual(verify_share_token(share_token), canonical_ticket.ticket_id)

        page_response = self.client.get(
            reverse('ticket_share', kwargs={'share_token': share_token})
        )
        self.assertEqual(page_response.status_code, 200)
        self.assertContains(page_response, 'Shared Event Ticket')
        self.assertContains(page_response, '3 tickets')

        qr_response = self.client.get(
            reverse('api_qr_generate', kwargs={'ticket_id': canonical_ticket.ticket_id}),
            {'share_token': share_token},
        )
        self.assertEqual(qr_response.status_code, 200)
        self.assertGreaterEqual(qr_response.json()['expires_in'], 1)
        self.assertLessEqual(qr_response.json()['expires_in'], 30)
        payload, _ = verify_token(qr_response.json()['token'])
        self.assertEqual(payload['ticket_id'], canonical_ticket.ticket_id)

    def test_share_link_rejects_tampering_and_qr_refresh_requires_owner_or_share(self):
        canonical_ticket = self.booking.tickets.order_by('pk').first()
        share_token = make_share_token(canonical_ticket.ticket_id)
        tampered_token = share_token[:-1] + ('a' if share_token[-1] != 'a' else 'b')

        invalid_page = self.client.get(
            reverse('ticket_share', kwargs={'share_token': tampered_token})
        )
        self.assertEqual(invalid_page.status_code, 404)

        self.client.logout()
        denied_qr = self.client.get(
            reverse('api_qr_generate', kwargs={'ticket_id': self.ticket.ticket_id})
        )
        self.assertEqual(denied_qr.status_code, 403)

    def test_share_page_reports_used_after_booking_validation(self):
        canonical_ticket = self.booking.tickets.order_by('pk').first()
        share_token = make_share_token(canonical_ticket.ticket_id)
        qr_token = make_token(self.ticket)
        self.client.force_login(self.organizer)

        validated = self.post_token(qr_token)
        self.assertEqual(validated.status_code, 200)

        self.client.logout()
        page_response = self.client.get(
            reverse('ticket_share', kwargs={'share_token': share_token})
        )
        self.assertEqual(page_response.status_code, 200, page_response.content.decode())
        self.assertContains(page_response, 'Ticket Already Used.')
        self.assertNotContains(page_response, 'shared-ticket-qr')

    def test_used_ticket_cannot_generate_a_new_qr(self):
        self.ticket.mark_as_used(self.organizer)
        self.client.force_login(self.user)

        response = self.client.get(
            reverse('api_qr_generate', kwargs={'ticket_id': self.ticket.ticket_id})
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json()['detail'], 'Ticket Already Used.')

    def test_qr_validation_requires_an_authenticated_organizer(self):
        token = make_token(self.ticket)
        self.client.logout()

        response = self.post_token(token)

        self.assertEqual(response.status_code, 403)

    def test_mobile_validation_link_loads_organizer_page(self):
        response = self.client.get(
            reverse('validate_ticket', kwargs={'slug': self.event.slug}),
            {'token': make_token(self.ticket)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Validating scanned QR code...')

    def test_native_camera_scan_shows_validity_without_consuming_for_attendee(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('qr_scan'), {'token': make_token(self.ticket)})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valid QR code — NOT CHECKED IN.')
        self.assertContains(response, 'authenticated organizer must check it in')
        self.assertContains(response, self.booking.booking_id)
        self.assertContains(response, 'Tickets booked:')
        self.assertContains(response, 'Tickets available:')
        self.assertContains(response, 'Your signed-in account is not authorized to scan this event.')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'valid')

    def test_different_organizer_cannot_check_in_event_ticket(self):
        other_organizer = User.objects.create_user(
            username='other-qr-organizer',
            password='testpass123',
        )
        other_organizer.profile.is_organizer = True
        other_organizer.profile.save()
        self.client.force_login(other_organizer)

        response = self.client.get(
            reverse('qr_scan'),
            {'token': make_token(self.ticket)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['can_validate'])
        self.assertContains(response, 'Your signed-in account is not authorized to scan this event.')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'valid')

    def test_organizer_scan_page_posts_checkin_and_next_scan_reports_used(self):
        token = make_token(self.ticket)

        first_scan_page = self.client.get(reverse('qr_scan'), {'token': token})
        self.assertEqual(first_scan_page.status_code, 200)
        self.assertTrue(first_scan_page.context['can_validate'])
        self.assertContains(first_scan_page, 'Checking this ticket in...')

        validation_response = self.post_token(token)
        self.assertEqual(validation_response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'used')

        second_scan_page = self.client.get(reverse('qr_scan'), {'token': token})
        self.assertEqual(second_scan_page.status_code, 200)
        self.assertContains(second_scan_page, 'ALREADY USED')
    def test_native_camera_scan_shows_expired_status(self):
        old_timestamp = int(timezone.now().timestamp()) - 60
        token = make_token(self.ticket, now_ts=old_timestamp)

        response = self.client.get(reverse('qr_scan'), {'token': token})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'QR Code Expired. Please Scan the Latest QR Code.')
        self.assertContains(response, self.booking.booking_id)

    def test_newly_refreshed_qr_is_accepted_after_previous_token_expires(self):
        now_ts = int(timezone.now().timestamp())
        expired_token = make_token(self.ticket, now_ts=now_ts - 30)
        refreshed_token = make_token(self.ticket, now_ts=now_ts)

        expired_response = self.post_token(expired_token)
        refreshed_response = self.post_token(refreshed_token)

        self.assertEqual(expired_response.status_code, 400)
        self.assertEqual(
            expired_response.json()['detail'],
            'QR Code Expired. Please Scan the Latest QR Code.',
        )
        self.assertEqual(refreshed_response.status_code, 200)
        self.assertEqual(refreshed_response.json()['detail'], 'VALID')

    def test_token_timestamp_uses_generation_time_not_refresh_bucket(self):
        generated_at = 1_793_000_017
        token = make_token(self.ticket, now_ts=generated_at)
        payload, _ = verify_token(token)

        self.assertEqual(payload['ts'], generated_at)

    def test_manual_verification_code_validation_still_works(self):
        self.client.login(username='qr-organizer', password='testpass123')

        with patch('events.views.render', return_value=HttpResponse()) as render:
            response = self.client.post(
                reverse('validate_ticket', kwargs={'slug': self.event.slug}),
                {'verification_code': self.ticket.verification_code},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(render.call_args.args[2]['ticket'], self.ticket)
        self.assertEqual(render.call_args.args[2]['ticket_validation_result'], 'validated')
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'used')
        self.assertTrue(TicketScanLog.objects.filter(
            ticket=self.ticket,
            scanner=self.organizer,
            success=True,
        ).exists())


# Run tests with: python manage.py test


class SeedDemoCommandTestCase(TestCase):
    """The demo seed creates upcoming published events and is safe to re-run."""

    def test_seed_demo_is_idempotent_and_upcoming(self):
        from django.core.management import call_command
        from io import StringIO
        import os
        os.environ['DEMO_PASSWORD'] = 'demo-test-pass-123'
        try:
            call_command('seed_demo', stdout=StringIO())
            call_command('seed_demo', stdout=StringIO())
        finally:
            del os.environ['DEMO_PASSWORD']
        events = Event.objects.filter(organizer__username='demo_organizer')
        self.assertEqual(events.count(), 12)
        self.assertFalse(events.filter(event_date__lt=timezone.localdate()).exists())
        self.assertTrue(User.objects.get(username='demo_organizer').profile.is_organizer)
        self.assertFalse(User.objects.get(username='demo_user').profile.is_organizer)
