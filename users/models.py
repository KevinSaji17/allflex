from django.db import models
from django.conf import settings

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
