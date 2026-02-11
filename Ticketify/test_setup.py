#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticketify_project.settings')
django.setup()

# Run checks
from django.core.management import execute_from_command_line
execute_from_command_line(['manage.py', 'check'])

print("\n✓ All checks passed!")
