# Generated by Django 3.1.7 on 2021-12-04 07:12

import django.contrib.postgres.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('ip', models.CharField(blank=True, max_length=255, null=True)),
                ('quantity', models.IntegerField(default=1)),
                ('price', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=255, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Keyword',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('keyword', models.CharField(max_length=255, null=True, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('email', models.EmailField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('product_title', models.CharField(max_length=255, null=True)),
                ('brand', models.CharField(max_length=255, null=True)),
                ('product_weight', models.CharField(blank=True, max_length=255, null=True)),
                ('short_description', models.TextField(blank=True, null=True)),
                ('charge_five_percent_vat', models.BooleanField()),
                ('return_policy', models.CharField(blank=True, max_length=255, null=True)),
                ('warranty', models.CharField(blank=True, max_length=255, null=True)),
                ('color', models.CharField(blank=True, max_length=255, null=True)),
                ('gender', models.CharField(blank=True, max_length=255, null=True)),
                ('keyword', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=250), size=None)),
                ('clicks', models.IntegerField(default=0)),
                ('promoted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('image_url', models.TextField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductOption',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('size', models.CharField(max_length=255, null=True)),
                ('quantity', models.CharField(max_length=255, null=True)),
                ('price', models.FloatField(null=True)),
                ('discounted_price', models.FloatField(null=True)),
                ('option_total_price', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProductPromotion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('start_date', models.CharField(max_length=255, null=True)),
                ('end_date', models.CharField(max_length=255, null=True)),
                ('days', models.IntegerField(null=True)),
                ('active', models.BooleanField(default=True, null=True)),
                ('amount', models.FloatField(null=True)),
                ('reach', models.IntegerField(default=0, null=True)),
                ('link_clicks', models.IntegerField(default=0, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('rating', models.IntegerField(null=True)),
                ('comment', models.TextField(blank=True, null=True)),
                ('like', models.PositiveIntegerField()),
                ('dislike', models.PositiveIntegerField()),
                ('rated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Wishlist',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('products', models.ManyToManyField(related_name='products_wished', to='market.Product')),
            ],
        ),
    ]
