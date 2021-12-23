# Generated by Django 3.1.7 on 2021-12-06 14:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('market', '0005_auto_20211206_1419'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='review',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='rating',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]