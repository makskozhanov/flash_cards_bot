from deck_actions import get_user_decks
from telebot.util import quick_markup
from telebot.types import InlineKeyboardMarkup
from redis_init import redis_db


async def show_menu(bot, message) -> None:
    """
    Shows menu to user with their decks
    :param bot:
    :param message:
    :return: None
    """
    print('MENU')
    user_id = message.from_user.id
    if not redis_db.exists(user_id):
        user_decks = get_user_decks(user_id)
        print(user_decks)
        redis_db.hset(user_id, mapping=user_decks)
    else:
        print('redis:', type(redis_db.hgetall(user_id)))
        user_decks = redis_db.hgetall(user_id)
    menu_markup = create_menu_markup(user_decks)
    await bot.send_message(message.chat.id, 'Меню', reply_markup=menu_markup)


def create_menu_markup(user_decks) -> InlineKeyboardMarkup:
    markup = {'Создать колоду': {'callback_data': 'create_deck'}}
    for name, deck_id in user_decks.items():
        markup[name] = {'callback_data': deck_id}
    return quick_markup(markup, row_width=1)


def insert_decks_into_cache(user_decks):
    for name, deck_id in enumerate(user_decks):
        redis_db.hset(1, mapping={name: deck_id})
