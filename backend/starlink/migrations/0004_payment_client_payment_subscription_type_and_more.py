# Generated by Django 5.1.7 on 2025-03-11 06:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starlink', '0003_plate_alter_payment_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='client',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='starlink.client', verbose_name='Пользователь'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='subscription_type',
            field=models.CharField(choices=[('standard', 'Стандарт - 15 000 ₽/мес.'), ('flat', 'Флэт - 63 000 ₽/мес.'), ('global', 'Глобал - 49 000 ₽/мес.')], default='standard', max_length=255, verbose_name='Тип подписки'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.IntegerField(choices=[(0, 'Не оплачено'), (1, 'Предавторизованная сумма захолдирована (для двухстадийных платежей)'), (2, 'Оплачено'), (3, 'Авторизация отменена'), (4, 'Оформлен возврат'), (5, 'Инициирована авторизация через ACS банка-эмитента'), (6, 'Авторизация отклонена')], verbose_name='Статус'),
        ),
    ]
