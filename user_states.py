from telebot.asyncio_handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    first_login = State()
    menu = State()
    create_deck = State()
    delete_deck = State()
    add_card_face = State()
    add_card_back = State()
    add_card_more = State()