import uuid
from django.db import models
from users.models import ExtendUser


# Create your models here.



class StoreDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(ExtendUser, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=225, unique=True, error_messages="Store with name already exists")
    email = models.EmailField(unique=True, error_messages="Store with email already exists")
    address = models.CharField(max_length=225)


class PurchasedItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="purchased_item")
    item = models.CharField(max_length=225)
    description = models.TextField()
    quantity = models.PositiveBigIntegerField()
    unit_cost = models.PositiveBigIntegerField()
    total = models.PositiveBigIntegerField()


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    store = models.ForeignKey(StoreDetail, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=225)
    customer_email = models.EmailField()
    customer_address = models.CharField(max_length=225)
    delivery_fee = models.PositiveBigIntegerField()
    subtotal = models.PositiveBigIntegerField()
    total = models.PositiveBigIntegerField()
    invoice_number = models.CharField(max_length=10)
    issue_date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=225, blank=True)

    def save(self, *args, **kwargs):
        while not self.invoice_number:
            number = Invoice.objects.count() + 1
            invoice_number = f"INV {number}"
            self.invoice_number = invoice_number

        super().save(*args, **kwargs)



class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    owner = models.OneToOneField(ExtendUser, on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(default=0)
    

class WalletTransaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transaction")
    remark = models.CharField(max_length=225)
    amount = models.PositiveBigIntegerField()
    date = models.DateField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10)
    status = models.BooleanField(default=False)