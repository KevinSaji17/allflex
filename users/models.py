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


class FavoriteGym(models.Model):
    """Track user's favorite gyms"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_gyms')
    gym = models.ForeignKey('gyms.Gym', on_delete=models.CASCADE, related_name='favorited_by', null=True, blank=True)
    gym_name = models.CharField(max_length=255, blank=True, help_text='For AI-generated gyms not in DB')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        name = self.gym.name if self.gym else self.gym_name
        return f"{self.user.username} favorited {name}"


class UserFitnessProfile(models.Model):
    """Track user's fitness progress and personal info"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fitness_profile')
    current_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Weight in kg")
    target_weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Target weight in kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Height in cm")
    age = models.PositiveIntegerField(null=True, blank=True)
    fitness_goal = models.CharField(max_length=100, blank=True, help_text="E.g., Weight loss, Muscle gain, General fitness")
    total_visits = models.PositiveIntegerField(default=0, help_text="Total gym visits")
    total_credits_spent = models.PositiveIntegerField(default=0, help_text="Total credits used")
    joined_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Fitness Profile"

    def bmi(self):
        """Calculate BMI if height and weight are available"""
        if self.height and self.current_weight:
            height_in_meters = float(self.height) / 100
            return round(float(self.current_weight) / (height_in_meters ** 2), 2)
        return None
