from aiogram import types
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist
from django.db import models


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
    username = models.CharField(verbose_name='Ник', max_length=32, null=True, blank=True)
    is_premium = models.BooleanField(
        verbose_name='Есть премиум',
        default=False,
    )
    kit_number = models.CharField(verbose_name='Кит номер тарелки', max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = ClientManager()

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-created_at']

    def __str__(self):
        return f'@{self.username}' if self.username else self.first_name


class Payment(models.Model):
    status = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    objects: models.Manager

    class Meta:
        verbose_name = 'Оплата'
        verbose_name_plural = 'Оплаты'
        ordering = ['-created_at']

    def __str__(self):
        return self.status


class SupportSection(models.Model):
    reason = models.TextField()
    solution = models.TextField()
    objects: models.Manager

    class Meta:
        verbose_name = 'Раздел тех. поддержки'
        verbose_name_plural = 'Разделы тех. поддержки'
        ordering = ['reason']

    def __str__(self):
        return self.reason[:100]


class Publication(models.Model):
    text = models.TextField()
    media = models.FileField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    objects: models.Manager

    class Meta:
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'
        ordering = ['-created_at']

    def __str__(self):
        return self.text[:100]
