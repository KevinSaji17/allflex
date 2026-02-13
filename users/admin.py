from django.contrib import admin
from .models import CreditPack, UserCreditBalance, CreditTransaction

# Register your models here.
admin.site.register(CreditPack)
admin.site.register(UserCreditBalance)
admin.site.register(CreditTransaction)
