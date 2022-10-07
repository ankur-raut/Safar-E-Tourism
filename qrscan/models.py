from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import CharField



class Tickett(models.Model):
    name=models.CharField(max_length=20)
    city=models.CharField(max_length=20)
    monument=models.CharField(max_length=20)
    date=models.DateField()
    email=models.EmailField()
    count=models.IntegerField()
    ticket_price=models.DecimalField(decimal_places=1,max_digits=7)
    total_cost=models.CharField(max_length=20)
    order_id = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    paid = models.BooleanField(default=False)
    timevalid=models.DateTimeField(blank=True, null=True)
    verified=models.BooleanField(default=False)
    def __str__(self):
        if self.paid:
            a="paid"
        else:
            a="unpaid"
        if self.verified:
            b="verified"
        else:
            b="unverified"
        return f"{self.name}-{a}-{b}"