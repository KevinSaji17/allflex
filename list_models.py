#!/usr/bin/env python
"""List available Gemini models"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'allflex.settings')
django.setup()

from django.conf import settings
import google.genai as genai

api_key = settings.GEMINI_API_KEY
client = genai.Client(api_key=api_key)

print("Available Gemini Models:")
print("=" * 60)

try:
    models = client.models.list()
    for model in models:
        print(f"- {model.name}")
        if hasattr(model, 'supported_generation_methods'):
            print(f"  Methods: {model.supported_generation_methods}")
except Exception as e:
    print(f"Error listing models: {e}")
