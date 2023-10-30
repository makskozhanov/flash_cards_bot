from deck_actions import GetDecks
from telebot.util import quick_markup
from telebot.types import InlineKeyboardMarkup
from redis_db.redis_init import redis_db
from menu.keyboard_layouts import no_decks_markup
from telebot.asyncio_helper import ApiTelegramException


async def show_menu(bot, message) -> None:
    """
    Shows menu to user with their decks
    :param bot:
    :param message:
    :return: None
    """

    user_id = message.chat.id
    record_name_in_cache = str(user_id) + ':decks'

    if not redis_db.exists(record_name_in_cache):  # Если нет колод в кэше - берем их из бд и сохраняем в кэш
        action = GetDecks(user_id)
        action.perform()

    user_decks = redis_db.hgetall(record_name_in_cache)

    if len(user_decks) > 0:
        menu_markup = create_menu_markup(user_decks)
    else:
        menu_markup = no_decks_markup

    await bot.send_message(message.chat.id, 'ㅤ\n<b>Главное меню</b>\nㅤ', reply_markup=menu_markup, parse_mode='html')


def create_menu_markup(user_decks) -> InlineKeyboardMarkup:
    markup = {'Создать колоду': {'callback_data': 'create_deck'}}
    for name, deck_id in user_decks.items():
        markup[name] = {'callback_data': deck_id}
    return quick_markup(markup, row_width=1)
