"""
Corrected comprehensive event updater:
- Cricket: Correct team stadiums (SRH in Uppal, etc.)
- Non-cricket Sports (Basketball, Tennis, Boxing, etc.): LB Stadium or Gachibowli
- Other events: Diverse Hyderabad locations
- Correct image URLs per category
- Generate report CSV for manual review

Usage:
    python scripts/update_events_corrected.py

Run from project root.
"""
import os
import sys
import csv
import decimal
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketify_project.settings')

import django
django.setup()

from events.models import Event, Category
from django.db import transaction

# Correct Cricket team → (Stadium Name, City, full address, Price)
CRICKET_STADIUMS = {
    'rcb': ('M. Chinnaswamy Stadium', 'Bangalore', 'M. Chinnaswamy Stadium, Bangalore, Karnataka, India', decimal.Decimal('1500.00')),
    'srh': ('Rajiv Gandhi International Cricket Stadium, Uppal', 'Hyderabad', 'Rajiv Gandhi International Cricket Stadium, Uppal, Hyderabad, Telangana, India', decimal.Decimal('1000.00')),
    'csk': ('M.A. Chidambaram Stadium', 'Chennai', 'M.A. Chidambaram Stadium, Chepauk, Chennai, Tamil Nadu, India', decimal.Decimal('1200.00')),
    'mi': ('Wankhede Stadium', 'Mumbai', 'Wankhede Stadium, Mumbai, Maharashtra, India', decimal.Decimal('2000.00')),
    'dc': ('Arun Jaitley Stadium', 'Delhi', 'Arun Jaitley Stadium (Feroz Shah Kotla), Delhi, India', decimal.Decimal('1200.00')),
    'kkr': ('Eden Gardens', 'Kolkata', 'Eden Gardens, Kolkata, West Bengal, India', decimal.Decimal('1100.00')),
    'pbks': ('Punjab Cricket Association Stadium', 'Mohali', 'Punjab Cricket Association Stadium, Mohali, Punjab, India', decimal.Decimal('900.00')),
    'rr': ('Sawai Mansingh Stadium', 'Jaipur', 'Sawai Mansingh Stadium, Jaipur, Rajasthan, India', decimal.Decimal('900.00')),
}

# Sports venues in Hyderabad
SPORTS_VENUES = {
    'lb_stadium': ('LB Stadium', 'Hyderabad', 'LB Nagar Stadium, LB Nagar, Hyderabad, Telangana, India', decimal.Decimal('1100.00')),
    'gachibowli': ('Gachibowli Stadium', 'Hyderabad', 'Gachibowli Stadium, Hyderabad, Telangana, India', decimal.Decimal('1200.00')),
}

# Other diverse Hyderabad locations
HYDERABAD_LOCATIONS = [
    ('Jubilee Hills', 'Hyderabad', 'Jubilee Hills, Hyderabad, Telangana, India', decimal.Decimal('1500.00')),
    ('Hi-Tech City, HITEC', 'Hyderabad', 'Hi-Tech City HITEC, Hyderabad, Telangana, India', decimal.Decimal('1200.00')),
    ('Kondapur', 'Hyderabad', 'Kondapur, Hyderabad, Telangana, India', decimal.Decimal('1100.00')),
    ('Begumpet', 'Hyderabad', 'Begumpet, Hyderabad, Telangana, India', decimal.Decimal('1300.00')),
    ('Kukatpally', 'Hyderabad', 'Kukatpally, Hyderabad, Telangana, India', decimal.Decimal('1000.00')),
    ('Banjara Hills', 'Hyderabad', 'Banjara Hills, Hyderabad, Telangana, India', decimal.Decimal('1400.00')),
    ('Secunderabad', 'Hyderabad', 'Secunderabad, Hyderabad, Telangana, India', decimal.Decimal('1100.00')),
    ('Somajiguda', 'Hyderabad', 'Somajiguda, Hyderabad, Telangana, India', decimal.Decimal('1250.00')),
    ('KPHB', 'Hyderabad', 'KPHB, Hyderabad, Telangana, India', decimal.Decimal('950.00')),
    ('Madhapur', 'Hyderabad', 'Madhapur, Hyderabad, Telangana, India', decimal.Decimal('1150.00')),
    ('Indiranagar', 'Hyderabad', 'Indiranagar, Hyderabad, Telangana, India', decimal.Decimal('1050.00')),
    ('Ameerpet', 'Hyderabad', 'Ameerpet, Hyderabad, Telangana, India', decimal.Decimal('1000.00')),
]

# Correct Image URLs by category/keyword
EVENT_IMAGES = {
    'cricket': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800&h=600&fit=crop',
    'ipl': 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=800&h=600&fit=crop',
    'basketball': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&h=600&fit=crop',
    'tennis': 'https://images.unsplash.com/photo-1554224311-beee415c15ac?w=800&h=600&fit=crop',
    'boxing': 'https://images.unsplash.com/photo-1512605857029-348e0b3f1ca0?w=800&h=600&fit=crop',
    'football': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&h=600&fit=crop',
    'nba': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800&h=600&fit=crop',
    'fifa': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800&h=600&fit=crop',
    'food': 'https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800&h=600&fit=crop',
    'music': 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800&h=600&fit=crop',
    'concert': 'https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=800&h=600&fit=crop',
    'python': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&h=600&fit=crop',
    'workshop': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=600&fit=crop',
    'tech': 'https://images.unsplash.com/photo-1540575467063-178a50c2df87?w=800&h=600&fit=crop',
    'hackathon': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=800&h=600&fit=crop',
    'ai': 'https://images.unsplash.com/photo-1677442d019cecf76da5ee6a826aae47fc537baea?w=800&h=600&fit=crop',
    'blockchain': 'https://images.unsplash.com/photo-1526374965328-7f5ae4e8a83f?w=800&h=600&fit=crop',
    'comedy': 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&h=600&fit=crop',
    'standup': 'https://images.unsplash.com/photo-1585699324551-f6c309eedeca?w=800&h=600&fit=crop',
    'musical': 'https://images.unsplash.com/photo-1514613535308-eb5400a3672c?w=800&h=600&fit=crop',
    'dance': 'https://images.unsplash.com/photo-1504384308090-c894fdcc538d?w=800&h=600&fit=crop',
    'theater': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=600&fit=crop',
    'film': 'https://images.unsplash.com/photo-1533109752211-118fcf4312f5?w=800&h=600&fit=crop',
    'movie': 'https://images.unsplash.com/photo-1536440136628-849c177e76a1?w=800&h=600&fit=crop',
    'wine': 'https://images.unsplash.com/photo-1510812431401-41d2cab2707d?w=800&h=600&fit=crop',
    'cooking': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800&h=600&fit=crop',
    'marathon': 'https://images.unsplash.com/photo-1461896836934-ffe607ba8211?w=800&h=600&fit=crop',
    'formula1': 'https://images.unsplash.com/photo-1605559424843-9e4c3a0a4d48?w=800&h=600&fit=crop',
    'art': 'https://images.unsplash.com/photo-1579783902614-e3fb5141b0cb?w=800&h=600&fit=crop',
    'photography': 'https://images.unsplash.com/photo-1612198188060-c7c2a3b66eae?w=800&h=600&fit=crop',
    'marketing': 'https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&h=600&fit=crop',
}

def get_cricket_stadium(title_lower):
    """Match cricket event to team and return stadium info."""
    for team_key, stadium_info in CRICKET_STADIUMS.items():
        if team_key in title_lower:
            return stadium_info
    return None

def is_sports_event(title_lower, category_name):
    """Check if this is a sports (non-cricket) event."""
    sports_keywords = ['basketball', 'tennis', 'boxing', 'marathon', 'nba', 'fifa', 'wimbledon', 'formula1', 'f1']
    for keyword in sports_keywords:
        if keyword in title_lower or keyword in category_name.lower():
            return True
    return False

def get_image_url(title, category_name):
    """Find appropriate image URL based on title and category."""
    title_lower = title.lower()
    category_lower = category_name.lower() if category_name else ''
    
    # Check title keywords first
    for keyword, url in EVENT_IMAGES.items():
        if keyword in title_lower:
            return url
    
    # Check category keywords
    for keyword, url in EVENT_IMAGES.items():
        if keyword in category_lower:
            return url
    
    # Default fallback
    return 'https://images.unsplash.com/photo-1492684223066-81342ee5ff30?w=800&h=600&fit=crop'

# Collect all updates for reporting
updates_log = []
sports_venue_index = 0
other_location_index = 0
updated_count = 0
errors = []

with transaction.atomic():
    events = Event.objects.all().order_by('id')
    
    for event in events:
        try:
            changed = False
            title_lower = event.title.lower()
            category_name = event.category.name if event.category else ''
            
            old_venue = event.venue
            old_city = event.city
            old_address = event.address
            old_price = event.price
            
            # Handle Cricket events with correct stadiums
            if 'cricket' in title_lower or 'ipl' in title_lower:
                stadium_info = get_cricket_stadium(title_lower)
                if stadium_info:
                    stadium, city, address, price = stadium_info
                    if event.venue != stadium or event.city != city or event.price != price:
                        event.venue = stadium
                        event.city = city
                        event.address = address
                        event.price = price
                        changed = True
            # Handle non-cricket sports (use LB Stadium or Gachibowli alternately)
            elif is_sports_event(title_lower, category_name):
                venue_key = 'lb_stadium' if sports_venue_index % 2 == 0 else 'gachibowli'
                sports_venue_index += 1
                venue, city, address, price = SPORTS_VENUES[venue_key]
                if event.venue != venue or event.city != city or event.price != price:
                    event.venue = venue
                    event.city = city
                    event.address = address
                    event.price = price
                    changed = True
            # All other events: cycle through diverse Hyderabad locations
            else:
                venue, city, address, price = HYDERABAD_LOCATIONS[other_location_index % len(HYDERABAD_LOCATIONS)]
                other_location_index += 1
                if event.venue != venue or event.city != city or event.price != price:
                    event.venue = venue
                    event.city = city
                    event.address = address
                    event.price = price
                    changed = True
            
            # Get recommended image URL
            image_url = get_image_url(event.title, category_name)
            
            if changed:
                event.save()
                updated_count += 1
                status = '✓ UPDATED'
            else:
                status = '- UNCHANGED'
            
            updates_log.append({
                'id': event.id,
                'title': event.title,
                'category': category_name,
                'venue': event.venue,
                'city': event.city,
                'address': event.address,
                'price': str(event.price),
                'image_url': image_url,
                'status': status,
            })
            
            print(f"{status}: {event.title}")
            print(f"  → {event.venue}, {event.city} | ₹{event.price}")
            print(f"  → Image: {image_url}\n")
        
        except Exception as ex:
            errors.append((event.id, event.title, str(ex)))
            print(f"✗ ERROR: {event.title}: {ex}\n")

# Write CSV report for manual review/editing
csv_filename = os.path.join(PROJECT_ROOT, 'EVENT_DETAILS_REPORT.csv')
with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['id', 'title', 'category', 'venue', 'city', 'address', 'price', 'image_url', 'status'])
    writer.writeheader()
    writer.writerows(updates_log)

print(f"\n{'='*80}")
print(f"SUMMARY:")
print(f"  Total events: {Event.objects.count()}")
print(f"  Updated: {updated_count}")
print(f"  Errors: {len(errors)}")
print(f"\nReport saved to: {csv_filename}")
print(f"\nNote: Image URLs are recommendations. To apply:")
print(f"  1. Edit EVENT_DETAILS_REPORT.csv and update image_url column")
print(f"  2. Or visit /admin/ to manually upload images for each event")
print(f"  3. Or run a bulk image update script using the CSV")
print(f"{'='*80}\n")

if errors:
    print("ERRORS:")
    for eid, etitle, err in errors:
        print(f"  ID {eid} ({etitle}): {err}")
