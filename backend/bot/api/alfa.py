from uuid import uuid4

from aiohttp import ClientSession

from bot.loader import logger
from bot.settings import settings


async def register_order(amount: int) -> dict:
    async with ClientSession(settings.ALFA_BASE_URL) as session:
        data = {
            'userName': settings.ALFA_USERNAME,
            'password': settings.ALFA_PASSWORD,
            'orderNumber': uuid4(),
            'amount': amount,
            'returnUrl': settings.ALFA_RETURN_URL,
        }
        async with session.post('register.do', data=data) as rsp:
            data = await rsp.json()
            logger.info(f'Registered order: {data}')
            return data


async def get_order_status(order_id: str) -> dict:
    async with ClientSession(settings.ALFA_BASE_URL) as session:
        data = {
            'userName': settings.ALFA_USERNAME,
            'password': settings.ALFA_PASSWORD,
            'orderId': order_id,
        }
        async with session.post('getOrderStatus.do', data=data) as rsp:
            data = await rsp.json()
            logger.info(f'Order status: {data}')
            return data
