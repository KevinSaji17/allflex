"""
Proxy models for admin dashboard display
These models don't store data - they just provide admin dashboard links
"""
from django.db import models


class GymAdminLink(models.Model):
    """
    Proxy model to show 'Gyms' section in admin dashboard
    This doesn't store any data - it's just a link to the MongoDB gym management page
    """
    class Meta:
        managed = False  # Don't create database table
        verbose_name = "Gym"
        verbose_name_plural = "Gyms"
        app_label = 'gyms'
        default_permissions = ()  # No add/change/delete permissions needed
