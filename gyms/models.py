from django.db import models
from django.conf import settings

class Gym(models.Model):
    TIER_CHOICES = (
        (1, 'Tier 1'),
        (2, 'Tier 2'),
        (3, 'Tier 3'),
        (4, 'Tier 4'),
    )
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='gyms')
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='gym_logos/', blank=True, null=True)
    description = models.TextField()
    location = models.CharField(max_length=255) # For Google Maps integration
    tier = models.IntegerField(choices=TIER_CHOICES)
    capacity = models.PositiveIntegerField(default=20)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(default=False)
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} booking at {self.gym.name}'

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    gym = models.ForeignKey(Gym, on_delete=models.CASCADE, related_name='reviews')
    stars = models.IntegerField()
    comment = models.TextField()

    def __str__(self):
        return f'Rating for {self.gym.name} by {self.user.username}'

class PayoutRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    gym_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payout request from {self.gym_owner.username} for {self.amount}'

class CreditPack(models.Model):
    TIER_CHOICES = (
        (1, 'Tier 1'),
        (2, 'Tier 2'),
        (3, 'Tier 3'),
        (4, 'Tier 4'),
    )
    
    name = models.CharField(max_length=255)
    tier = models.IntegerField(choices=TIER_CHOICES)
    credits = models.PositiveIntegerField(help_text="Number of gym visit credits")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    validity_days = models.PositiveIntegerField(help_text="Number of days the pack is valid for")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['tier', 'price']

    def __str__(self):
        return f'{self.name} - {self.credits} credits (Tier {self.tier})'

class UserCreditPack(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='credit_packs')
    credit_pack = models.ForeignKey(CreditPack, on_delete=models.CASCADE)
    remaining_credits = models.PositiveIntegerField()
    purchased_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-purchased_at']

    def __str__(self):
        return f'{self.user.username} - {self.remaining_credits} credits remaining'

    def is_expired(self):
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def deduct_credit(self):
        if self.remaining_credits > 0 and not self.is_expired():
            self.remaining_credits -= 1
            if self.remaining_credits == 0:
                self.is_active = False
            self.save()
            return True
        return False
