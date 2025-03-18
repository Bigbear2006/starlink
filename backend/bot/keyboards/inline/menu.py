from bot.keyboards.inline.authorized import get_authorized_keyboard
from bot.keyboards.inline.unauthorized import unauthorized_kb
from starlink.models import Client


def get_menu_keyboard(client: Client):
    return get_authorized_keyboard(client) \
        if client.kit_number else unauthorized_kb
