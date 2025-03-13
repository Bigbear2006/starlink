import asyncio
import os

import django
from aiogram import F
from aiogram.types import BotCommand

from bot.loader import bot, dp, logger


async def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    django.setup()

    from bot.handlers import (
        auth,
        buy,
        commands,
        connect,
        faq,
        subscription,
        support,
    )

    dp.include_routers(
        commands.router,
        auth.router,
        buy.router,
        connect.router,
        subscription.router,
        faq.router,
        support.router,
    )
    dp.message.filter(F.chat.type == 'private')

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command='/start', description='Запустить бота'),
            BotCommand(command='/menu', description='Главное меню'),
            BotCommand(command='/connect', description='Подключить тарелку'),
            BotCommand(
                command='/subscription',
                description='Сроки подключения и абонентская плата',
            ),
            BotCommand(command='/buy', description='Приобрести тарелку'),
            BotCommand(
                command='/auth',
                description='Авторизоваться по кит номеру тарелки',
            ),
            BotCommand(
                command='/support',
                description='Техническая поддержка',
            ),
            BotCommand(command='/faq', description='FAQ'),
        ],
    )

    logger.info('Starting bot...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
