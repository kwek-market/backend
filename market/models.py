from django.db import models

# Create your models here.

class Category(models.Model):
    sub_category = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=255, blank=False, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    parentcategory = models.CharField(max_length=255, blank=True, null=True)
    childcategory = models.CharField(max_length=255, blank=True, null=True)
    parent = models.BooleanField(blank=False)
    child = models.BooleanField(blank=False)

    def __str__(self):
        return self.name

class Keyword(models.Model):
    keyword = models.CharField(max_length=255, blank=False, null=True)

    def __str__(self):
        return self.keyword


class Product(models.Model):
    product_title = models.CharField(max_length=255, blank=False, null=True)
    user = models.ForeignKey("users.ExtendUser", on_delete=models.CASCADE, null=True)
    category = models.ForeignKey("market.Subcategory", on_delete=models.CASCADE, null=True)
    brand = models.CharField(max_length=255, blank=False, null=True)
    product_weight = models.CharField(max_length=255, blank=True, null=True)
    short_description = models.TextField(blank=True,null=True)
    charge_five_percent_vat = models.BooleanField(blank=False)
    return_policy = models.CharField(max_length=255, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=255, blank=True, null=True)
    keyword = models.ManyToManyField("market.Keyword", related_name="keywords")
    clicks  = models.IntegerField(default=0, blank=False)
    promoted  = models.BooleanField(default=False, blank=False)

    def __str__(self):
        return self.product_title

class ProductImage(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    image_url = models.TextField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductOption(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    size = models.CharField(max_length=255, blank=False, null=True)
    quantity = models.CharField(max_length=255, blank=False, null=True)
    price = models.FloatField(blank=False, null=True)
    discounted_price = models.FloatField(blank=False, null=True)
    option_total_price = models.FloatField(blank=False, null=True)

    def __str__(self):
        return self.product


class ProductPromotion(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    start_date = models.CharField(max_length=255, blank=False, null=True)
    end_date = models.CharField(max_length=255, blank=False, null=True)
    days  = models.IntegerField(blank=False, null=True)
    active  = models.BooleanField(default=True,blank=False, null=True)
    amount = models.FloatField(blank=False, null=True)
    reach = models.IntegerField(default=0,blank=False, null=True)
    link_clicks = models.IntegerField(default=0,blank=False, null=True)

    def __str__(self):
        return self.keyword

class Rating(models.Model):
    product = models.ForeignKey("market.Product", on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(blank=False, null=True)
    comment = models.TextField(blank=True,null=True)
    name = models.CharField(max_length=255, blank=False, null=True)
    email = models.EmailField(blank=False, null=True)
    rated_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product
