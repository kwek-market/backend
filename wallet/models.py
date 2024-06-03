import uuid
from django.db import models
from users.models import ExtendUser
from bill.models import Order
from market.models import CartItem

# Create your models here.



class StoreDetail(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(ExtendUser, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=225, unique=True, error_messages={"unique":"Store with name already exists"})
    email = models.EmailField(unique=True, error_messages={"unique":"Store with email already exists"})
    address = models.CharField(max_length=225)


class PurchasedItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    invoice = models.ForeignKey("Invoice", on_delete=models.CASCADE, related_name="purchased_item")
    item = models.CharField(max_length=225)
    description = models.TextField(default="")
    quantity = models.PositiveBigIntegerField(default=1)
    unit_cost = models.PositiveBigIntegerField(blank=False)
    total = models.PositiveBigIntegerField(blank=False)


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    store = models.ForeignKey(StoreDetail, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=225)
    customer_email = models.EmailField(default="")
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
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=10)
    status = models.BooleanField(default=False)
    class Meta:
        indexes = [
            models.Index(fields=["-date"])
        ]

class WalletRefund(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='walletrefund')
    account_number = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    product = models.ForeignKey(CartItem, on_delete=models.CASCADE, null=True)
    number_of_product = models.IntegerField(default=1)
    status = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
