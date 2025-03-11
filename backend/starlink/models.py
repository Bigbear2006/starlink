from datetime import datetime

from aiogram import types
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import IntegerChoices, TextChoices

from bot.settings import settings


class User(AbstractUser):
    pass


class ClientManager(models.Manager):
    async def from_tg_user(self, user: types.User) -> 'Client':
        return await self.acreate(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def update_from_tg_user(self, user: types.User) -> None:
        await self.filter(pk=user.id).aupdate(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_premium=user.is_premium or False,
        )

    async def create_or_update_from_tg_user(
            self,
            user: types.User,
    ) -> tuple['Client', bool]:
        try:
            client = await self.aget(pk=user.id)
            await self.update_from_tg_user(user)
            await client.arefresh_from_db()
            return client, False
        except ObjectDoesNotExist:
            return await self.from_tg_user(user), True


class Client(models.Model):
    id = models.PositiveBigIntegerField(
        verbose_name='Телеграм ID',
        primary_key=True,
    )
    first_name = models.CharField(verbose_name='Имя', max_length=255)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=255,
        null=True,
        blank=True,
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=32,
        null=True,
        blank=True,
    )
    is_premium = models.BooleanField(
        verbose_name='Есть премиум',
        default=False,
    )
    kit_number = models.CharField(
        verbose_name='Кит номер тарелки',
        max_length=255,
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ClientManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f'@{self.username}' if self.username else self.first_name


class PaymentChoices(IntegerChoices):
    REGISTERED = 0, 'Не оплачено'
    ON_HOLD = 1, 'Предавторизованная сумма захолдирована ' \
                 '(для двухстадийных платежей)'
    SUCCESS = 2, 'Оплачено'
    AUTH_CANCELLED = 3, 'Авторизация отменена'
    REFUND = 4, 'Оформлен возврат'
    ACS_AUTH = 5, 'Инициирована авторизация через ACS банка-эмитента'
    AUTH_REJECTED = 6, 'Авторизация отклонена'


class SubscriptionPlanChoices(TextChoices):
    STANDARD = 'standard', 'Стандарт - 15 000 ₽/мес.'
    FLAT = 'flat', 'Флэт - 63 000 ₽/мес.'
    GLOBAL = 'global', 'Глобал - 49 000 ₽/мес.'


class Payment(models.Model):
    status = models.IntegerField(verbose_name='Статус', choices=PaymentChoices)
    subscription_plan = models.CharField(
        verbose_name='Тип подписки',
        max_length=255,
        choices=SubscriptionPlanChoices,
    )
    date = models.DateTimeField(
        verbose_name='Дата оплаты',
        null=True,
        blank=True,
    )
    client = models.ForeignKey(
        Client,
        models.CASCADE,
        'payments',
        verbose_name='Пользователь',
    )
    objects: models.Manager

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'
        ordering = ['-date']

    def __str__(self):
        return f'{datetime.strftime(self.date, settings.DATE_FMT)} ' \
               f'({PaymentChoices(self.status).label})'


class SupportSection(models.Model):
    reason = models.TextField(verbose_name='Причина')
    solution = models.TextField(verbose_name='Решение')
    objects: models.Manager

    class Meta:
        verbose_name = 'Раздел тех. поддержки'
        verbose_name_plural = 'Разделы тех. поддержки'
        ordering = ['reason']

    def __str__(self):
        return self.reason[:50]


class Publication(models.Model):
    text = models.TextField(verbose_name='Текст')
    media = models.FileField(
        verbose_name='Фото или видео',
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True,
    )
    objects: models.Manager

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:100]


class Plate(models.Model):
    model = models.CharField(verbose_name='Модель', max_length=255)
    photo = models.ImageField(verbose_name='Фото', upload_to='starlink')
    price = models.IntegerField(verbose_name='Цена')
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Тарелка'
        verbose_name_plural = 'Тарелки'
        ordering = ['model']

    def __str__(self):
        return self.model
