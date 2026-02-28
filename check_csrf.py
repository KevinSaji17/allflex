#!/usr/bin/env python
"""
CSRF Login Debug Script
Helps diagnose CSRF issues with login
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.conf import settings

print("=" * 70)
print("CSRF Configuration Check")
print("=" * 70)
print()

print("Django Settings:")
print(f"  DEBUG: {settings.DEBUG}")
print(f"  ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print()

print("CSRF Settings:")
print(f"  CSRF_COOKIE_HTTPONLY: {getattr(settings, 'CSRF_COOKIE_HTTPONLY', 'Not Set')}")
print(f"  CSRF_COOKIE_SAMESITE: {getattr(settings, 'CSRF_COOKIE_SAMESITE', 'Not Set')}")
print(f"  CSRF_TRUSTED_ORIGINS: {getattr(settings, 'CSRF_TRUSTED_ORIGINS', 'Not Set')}")
print(f"  CSRF_USE_SESSIONS: {getattr(settings, 'CSRF_USE_SESSIONS', 'Not Set')}")
print()

print("Session Settings:")
print(f"  SESSION_COOKIE_AGE: {settings.SESSION_COOKIE_AGE} seconds ({settings.SESSION_COOKIE_AGE // 86400} days)")
print(f"  SESSION_COOKIE_SAMESITE: {getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Not Set')}")
print(f"  SESSION_COOKIE_HTTPONLY: {getattr(settings, 'SESSION_COOKIE_HTTPONLY', 'Not Set')}")
print(f"  SESSION_EXPIRE_AT_BROWSER_CLOSE: {settings.SESSION_EXPIRE_AT_BROWSER_CLOSE}")
print()

print("Middleware Order:")
for i, middleware in enumerate(settings.MIDDLEWARE, 1):
    print(f"  {i}. {middleware}")
print()

print("=" * 70)
print("Common CSRF Issues & Solutions")
print("=" * 70)
print()
print("1. Clear Browser Cookies:")
print("   - Open browser DevTools (F12)")
print("   - Go to Application/Storage tab")
print("   - Clear all cookies for localhost:8000")
print()
print("2. Hard Refresh:")
print("   - Press Ctrl + Shift + R (Windows/Linux)")
print("   - Or Cmd + Shift + R (Mac)")
print()
print("3. Try Incognito/Private Window:")
print("   - Opens clean session without cached cookies")
print()
print("4. Check Browser Console:")
print("   - F12 → Console tab")
print("   - Look for any JavaScript errors")
print()
print("5. Restart Django Server:")
print("   - Stop server (Ctrl+C)")
print("   - Run: python manage.py runserver")
print()

