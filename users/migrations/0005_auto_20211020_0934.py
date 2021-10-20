# Generated by Django 3.1.7 on 2021-10-20 08:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20210725_0919'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='category',
        ),
        migrations.RemoveField(
            model_name='product',
            name='keyword',
        ),
        migrations.RemoveField(
            model_name='product',
            name='user',
        ),
        migrations.RemoveField(
            model_name='productimage',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productoption',
            name='product',
        ),
        migrations.RemoveField(
            model_name='productpromotion',
            name='product',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='product',
        ),
        migrations.RemoveField(
            model_name='subcategory',
            name='category',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Keyword',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.DeleteModel(
            name='ProductImage',
        ),
        migrations.DeleteModel(
            name='ProductOption',
        ),
        migrations.DeleteModel(
            name='ProductPromotion',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.DeleteModel(
            name='Subcategory',
        ),
    ]
