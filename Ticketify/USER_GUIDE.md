# Ticketify User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [For Event Attendees](#for-event-attendees)
3. [For Event Organizers](#for-event-organizers)
4. [Admin Panel](#admin-panel)
5. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

1. **Install Python 3.8+** (if not already installed)
   - Download from https://www.python.org/downloads/

2. **Open Command Prompt/Terminal** in the Ticketify folder

3. **Run the Quick Start**:
   ```bash
   python quickstart.py
   ```
   
   Or use the batch file on Windows:
   ```bash
   start_server.bat
   ```

4. **Access the Website**:
   - Open browser: http://127.0.0.1:8000/

---

## For Event Attendees

### Creating an Account

1. Click **"Sign Up"** in the navigation bar
2. Fill in your details:
   - Username
   - Email
   - Password
   - Name
   - Phone (optional)
3. Click **"Create Account"**
4. You'll be automatically logged in

### Browsing Events

1. **Homepage**: View featured and upcoming events
2. **Events Page**: Browse all available events
3. **Use Filters**:
   - Search by keyword
   - Filter by category
   - Filter by date (today, tomorrow, weekend, etc.)
   - Filter by price (free or paid)
   - Sort by date, price, or popularity

### Booking Tickets

1. **Find an Event**: Browse or search for events
2. **View Details**: Click on an event to see full details
3. **Click "Book Now"**
4. **Select Quantity**: Choose number of tickets
5. **Enter Details**: Confirm email and phone
6. **Confirm Booking**: Review and confirm your order
7. **Receive Tickets**: Get instant confirmation with QR codes

### Viewing Your Tickets

1. Go to **"My Tickets"** from the user menu
2. See all your purchased tickets
3. Click **"View Full Ticket"** to see:
   - QR code
   - Event details
   - Ticket status
4. **Print or Screenshot** your ticket

### Using Your Ticket

1. **Save your QR code** (screenshot or print)
2. **Arrive at the event** 15-30 minutes early
3. **Show your QR code** at the entrance
4. Staff will scan it for instant verification
5. **Enter and enjoy!**

### Reviewing Events

1. After attending an event, go to the event page
2. Click **"Write a Review"**
3. Rate the event (1-5 stars)
4. Add your comments
5. Submit your review

---

## For Event Organizers

### Becoming an Organizer

1. During registration, check **"Register as Event Organizer"**
2. Or contact admin to upgrade your account

### Accessing Organizer Dashboard

1. Login to your account
2. Click your username → **"Organizer Dashboard"**
3. View statistics:
   - Total events
   - Published events
   - Total bookings
   - Total revenue

### Creating an Event

1. Go to **Organizer Dashboard**
2. Click **"Create New Event"**
3. Fill in event details:

   **Basic Information**:
   - Title: Event name
   - Slug: URL-friendly name (auto-generated)
   - Description: Detailed description
   - Category: Select appropriate category
   - Image: Upload event poster/image

   **Location Details**:
   - Venue name
   - Full address
   - City

   **Date & Time**:
   - Start date and time
   - End date and time

   **Pricing & Capacity**:
   - Price per ticket (set to 0 for free events)
   - Total number of tickets

   **Status**:
   - Draft: Not visible to public
   - Published: Visible and bookable
   - Cancelled: Event cancelled
   - Completed: Event finished
   
   **Featured**: Check to feature on homepage

4. Click **"Create Event"**

### Managing Your Events

1. **View Events**: See all your events in dashboard
2. **Edit Event**: Click edit icon to modify details
3. **View Bookings**: Click ticket icon to see all bookings
4. **Validate Tickets**: Click QR icon to validate at entrance
5. **Delete Event**: Click delete button (only if no bookings)

### Monitoring Ticket Sales

1. Go to **Organizer Dashboard**
2. See recent events with:
   - Tickets sold / Total tickets
   - Sales progress bar
   - Percentage sold
3. Click **"View Bookings"** for detailed list:
   - Customer information
   - Booking IDs
   - Ticket quantities
   - Payment amounts
   - Booking dates

### Validating Tickets at Events

**Setup**:
1. On event day, go to **"Validate Tickets"** for your event
2. Have a device ready (phone, tablet, laptop)

**Validation Process**:
1. Ask attendee to show their QR code ticket
2. **Scan QR code** or **Enter verification code manually**
3. System will show:
   - ✅ **Valid**: Green message - Allow entry
   - ⚠️ **Already Used**: Yellow warning - Ticket already scanned
   - ❌ **Invalid**: Red error - Deny entry

4. View ticket details:
   - Ticket ID
   - Attendee name
   - Booking information

**Tips**:
- Test the system before event starts
- Have a backup device ready
- Keep the validation page open
- Record attendee count manually as backup

---

## Admin Panel

### Accessing Admin Panel

1. Go to: http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Access full administrative controls

### Admin Capabilities

**User Management**:
- View all users
- Change user details
- Set organizer status
- Manage permissions

**Event Management**:
- View all events
- Edit any event
- Delete events
- Manage categories

**Booking Management**:
- View all bookings
- Change booking status
- Issue refunds
- View statistics

**Ticket Management**:
- View all tickets
- Check validation status
- Manage ticket issues

**Category Management**:
- Create new categories
- Edit categories
- Set category icons

**Review Management**:
- Moderate reviews
- Delete inappropriate reviews
- View all ratings

---

## Troubleshooting

### Common Issues

**1. Can't Access Website**
- Ensure server is running: `python manage.py runserver`
- Check URL: http://127.0.0.1:8000/
- Try different browser
- Clear browser cache

**2. QR Codes Not Generating**
- Check Pillow is installed: `pip install Pillow`
- Ensure media folder exists
- Check file permissions

**3. Login Issues**
- Verify username and password
- Check Caps Lock
- Reset password via admin if needed

**4. Booking Not Working**
- Ensure you're logged in
- Check if tickets are available
- Verify event is published
- Try different payment details

**5. Can't Create Events**
- Confirm you're registered as organizer
- Check all required fields
- Ensure slug is unique
- Verify dates are in future

**6. Ticket Validation Failing**
- Check internet connection
- Verify you're logged in as organizer
- Ensure it's your event
- Try entering code manually

### Database Issues

**Reset Database** (WARNING: Deletes all data):
```bash
python manage.py flush
python manage.py migrate
python manage.py createsuperuser
python manage.py shell < setup_data.py
```

**Backup Database**:
```bash
copy db.sqlite3 db.sqlite3.backup
```

### Getting Help

1. Check README.md for detailed documentation
2. Review error messages carefully
3. Check Django logs in terminal
4. Verify all dependencies are installed
5. Contact support: support@ticketify.com

---

## Best Practices

### For Attendees
- Book tickets early for popular events
- Save multiple copies of QR codes
- Arrive 15-30 minutes before event
- Read event details carefully
- Keep booking confirmation emails

### For Organizers
- Add detailed event descriptions
- Upload high-quality images
- Set realistic capacities
- Publish events well in advance
- Test ticket validation before event
- Monitor sales regularly
- Respond to attendee questions

### Security Tips
- Use strong passwords
- Don't share QR codes publicly
- Keep booking confirmations private
- Report suspicious activity
- Logout from shared devices

---

## Features Summary

✅ **Secure Authentication**
✅ **Event Browsing & Search**
✅ **Online Ticket Booking**
✅ **QR Code Generation**
✅ **Instant Ticket Delivery**
✅ **Ticket Validation System**
✅ **Real-Time Inventory**
✅ **Organizer Dashboard**
✅ **Sales Analytics**
✅ **Event Management**
✅ **Review & Rating System**
✅ **Responsive Design**
✅ **Admin Panel**

---

**Need More Help?**
- Documentation: README.md
- Email: support@ticketify.com
- Website: http://127.0.0.1:8000/contact/

**Version**: 1.0.0
**Last Updated**: February 2026
