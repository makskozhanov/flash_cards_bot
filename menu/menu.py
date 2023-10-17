from deck_actions import get_user_decks
from telebot.util import quick_markup
from telebot.types import InlineKeyboardMarkup
from redis_db.redis_init import redis_db


async def show_menu(bot, message) -> None:
    """
    Shows menu to user with their decks
    :param bot:
    :param message:
    :return: None
    """
    print('MENU')
    user_id = message.from_user.id
    record_name_in_cache = str(user_id) + ':decks'
    if not redis_db.exists(record_name_in_cache):
        user_decks = get_user_decks(user_id)
        redis_db.hset(record_name_in_cache, mapping=user_decks)
    else:
        user_decks = redis_db.hgetall(record_name_in_cache)
    menu_markup = create_menu_markup(user_decks)
    await bot.send_message(message.chat.id, 'Меню', reply_markup=menu_markup)


def create_menu_markup(user_decks) -> InlineKeyboardMarkup:
    markup = {'Создать колоду': {'callback_data': 'create_deck'}}
    for name, deck_id in user_decks.items():
        markup[name] = {'callback_data': deck_id}
    return quick_markup(markup, row_width=1)
