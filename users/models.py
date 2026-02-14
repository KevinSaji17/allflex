from django.db import models
from django.conf import settings
from django.utils import timezone

TIER_CREDIT_COSTS = {1: 5, 2: 9, 3: 13, 4: 18}

# Create your models here.

class CreditPack(models.Model):
    name = models.CharField(max_length=50)
    credits = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_best_value = models.BooleanField(default=False)

    def price_per_credit(self):
        return round(self.price / self.credits, 2)

    def __str__(self):
        return f"{self.name} ({self.credits} credits)"

class UserCreditBalance(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_balance')
    credits = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}: {self.credits} credits"

class CreditTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('purchase', 'Purchase'),
        ('visit', 'Visit'),
        ('adjustment', 'Adjustment'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pack = models.ForeignKey(CreditPack, on_delete=models.SET_NULL, null=True, blank=True)
    gym = models.ForeignKey('gyms.Gym', on_delete=models.SET_NULL, null=True, blank=True)
    credits = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} {self.transaction_type} {self.credits} credits"


class GymBooking(models.Model):
    STATUS_CHOICES = (
        ('booked', 'Booked'),
        ('cancelled', 'Cancelled'),
        ('checked_in', 'Checked In'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gym_bookings')
    gym = models.ForeignKey('gyms.Gym', on_delete=models.CASCADE, related_name='bookings')
    tier = models.PositiveSmallIntegerField(default=1)
    credits_charged = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    booked_at = models.DateTimeField(default=timezone.now)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f"{self.user.username} booking at {self.gym.name}"
