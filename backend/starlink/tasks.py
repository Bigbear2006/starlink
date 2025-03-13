import asyncio
from datetime import datetime, timedelta

import magic
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter
from aiogram.types import BufferedInputFile
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import (
    Count,
    DateTimeField,
    OuterRef,
    Subquery,
)

from bot.keyboards.utils import one_button_keyboard
from bot.loader import bot
from starlink.models import Client, Payment

task_logger = get_task_logger(__name__)


def handle_send_message_errors(send_message_func):
    async def decorator(chat_id: int):
        try:
            await send_message_func(chat_id)
        except TelegramRetryAfter as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of rate limit',
            )
            await asyncio.sleep(e.retry_after)
            await send_message_func(chat_id)
        except TelegramBadRequest as e:
            task_logger.info(
                f'Cannot send a message to user (id={chat_id}) '
                f'because of an {e.__class__.__name__} error: {str(e)}',
            )
    return decorator


@shared_task
def send_publication(text: str, media_url: str = None):
    async def main():
        @handle_send_message_errors
        async def send_message(chat_id: int):
            if media_url:
                media_type = magic.from_file(media_url, mime=True)
                media = BufferedInputFile.from_file(media_url)
            else:
                media_type = ''
                media = None

            if media_type.startswith('image/'):
                await bot.send_photo(
                    chat_id,
                    media,
                    caption=text,
                )
            elif media_type.startswith('video/'):
                await bot.send_video(
                    chat_id,
                    media,
                    caption=text,
                )
            else:
                await bot.send_message(chat_id, text)

        await asyncio.wait(
            [
                asyncio.create_task(send_message(client.pk))
                async for client in Client.objects.all()
            ],
        )

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    loop.run_until_complete(main())


@shared_task
def send_reminders():
    async def main():
        @handle_send_message_errors
        async def send_message(chat_id: int):
            await bot.send_message(
                chat_id,
                'Ваша подписка истекает через 3 дня.\n'
                'Продлите её, чтобы избежать отключения своего Starlink.',
                reply_markup=one_button_keyboard(
                    text='Продлить',
                    callback_data='prolong_subscription',
                ),
            )

        # three_days_ago = (datetime.now(settings.TZ)
        # - timedelta(days=27)).date
        # payments = Payment.objects.filter(date__date=three_days_ago)
        # task_logger.info(
        #     f'Found {len(payments)} payments that expires in three days',
        # )
        client_payments = Payment.objects.values('client').annotate(
            earliest_payment=Subquery(
                Payment.objects
                .filter(client=OuterRef('client'))
                .order_by('date')[:1]
                .values('date'),
                output_field=DateTimeField(),
            ),
            payments_count=Count('id'),
        )

        clients_ids = []
        async for i in client_payments:
            subscription_end_date = (
                i['earliest_payment']
                 + timedelta(days=30 * i['payments_count'])
            ).date()
            # task_logger.info(
            #     f'END: {subscription_end_date}; '
            #     f'{subscription_end_date + timedelta(days=3)}'
            #     f'{subscription_end_date + timedelta(days=3) ==
            #     datetime.utcnow().date()}'
            # )
            if subscription_end_date + timedelta(days=3) == \
                    datetime.utcnow().date():
                clients_ids.append(i['client'])

        task_logger.info(clients_ids)
        await asyncio.wait(
            [
                asyncio.create_task(send_message(client_id))
                for client_id in clients_ids
            ],
        )

    loop = asyncio.get_event_loop()
    if loop.is_closed():
        loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
