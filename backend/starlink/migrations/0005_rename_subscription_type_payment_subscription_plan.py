# Generated by Django 5.1.7 on 2025-03-11 08:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('starlink', '0004_payment_client_payment_subscription_type_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='payment',
            old_name='subscription_type',
            new_name='subscription_plan',
        ),
    ]
