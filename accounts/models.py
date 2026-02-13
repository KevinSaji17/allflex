from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'User'),
        ('gym_owner', 'Gym Owner'),
        ('admin', 'Admin'),
    )
    PLAN_CHOICES = (
        ('basic', 'Basic'),
        ('plus', 'Plus'),
        ('pro', 'Pro'),
        ('elite', 'Elite'),
        ('none', 'None'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='none')
    credits = models.PositiveIntegerField(default=0)
    streak = models.PositiveIntegerField(default=0)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def __str__(self):
        return self.username


class CreditPackPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    credits_amount = models.PositiveIntegerField()
    purchase_amount = models.DecimalField(max_digits=6, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.credits_amount} credits purchased by {self.user.username}'
