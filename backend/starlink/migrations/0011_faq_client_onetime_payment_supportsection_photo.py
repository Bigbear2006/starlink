# Generated by Django 5.1.7 on 2025-03-17 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('starlink', '0010_alter_payment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(verbose_name='Текст')),
            ],
            options={
                'verbose_name': 'Часто задаваемые вопросы',
                'verbose_name_plural': 'Часто задаваемые вопросы',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='client',
            name='onetime_payment',
            field=models.BooleanField(default=False, verbose_name='Внесен единоразовый платеж'),
        ),
        migrations.AddField(
            model_name='supportsection',
            name='photo',
            field=models.ImageField(default='support/restricted.jpg', upload_to='support', verbose_name='Картинка'),
            preserve_default=False,
        ),
    ]
