#!/usr/bin/env python
"""
Fix cricket event cities to match their stadiums
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketify_project.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from events.models import Event

# Stadium to City mapping
STADIUM_CITY_MAP = {
    'Wankhede Stadium': 'Mumbai',
    'M. Chinnaswamy Stadium': 'Bangalore',
    'Eden Gardens': 'Kolkata',
    'Narendra Modi Stadium': 'Ahmedabad',
    'M.A. Chidambaram Stadium': 'Chennai',
    'Rajiv Gandhi Int\'l Cricket Stadium, Uppal': 'Hyderabad',
    'Arun Jaitley Stadium': 'Delhi',
    'PCA Stadium': 'Mohali',
    'Sawai Mansingh Stadium': 'Jaipur',
}

print("\n🔧 FIXING CRICKET EVENT CITIES\n" + "="*50)

# Get all cricket events with incorrect city
updated_count = 0
for stadium, correct_city in STADIUM_CITY_MAP.items():
    events = Event.objects.filter(venue=stadium, category__name='Sports')
    for event in events:
        if event.city != correct_city:
            old_city = event.city
            event.city = correct_city
            event.save()
            updated_count += 1
            print(f"✓ FIXED: {event.title}")
            print(f"  Venue: {stadium}")
            print(f"  City: {old_city} → {correct_city}\n")

print(f"\n{'='*50}")
print(f"Total cricket events fixed: {updated_count}")
print(f"Status: Complete ✓")
