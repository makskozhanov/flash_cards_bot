from telebot.asyncio_handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    firstLogin = State()
    menu = State()
    create_deck = State()
    add_card = State()

