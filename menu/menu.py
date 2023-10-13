from deck_actions import get_user_decks
from telebot.util import quick_markup
from telebot.types import InlineKeyboardMarkup


async def show_menu(bot, message) -> None:
    """
    Shows menu to user with their decks
    :param bot:
    :param message:
    :return: None
    """
    user_decks = get_user_decks(message.from_user.id)
    menu_markup = create_menu_markup(user_decks)
    await bot.send_message(message.chat.id, 'Меню', reply_markup=menu_markup)


def create_menu_markup(user_decks) -> InlineKeyboardMarkup:
    markup = {}
    for deck in user_decks:
        markup[deck.name] = {'callback_data': deck.id}
    return quick_markup(markup)

