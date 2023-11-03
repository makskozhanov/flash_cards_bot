"""
This file defines the user states needed to assign handlers.
"""


from telebot.asyncio_handler_backends import State, StatesGroup


class UserStates(StatesGroup):
    first_login = State()
    menu = State()
    create_deck = State()
    delete_deck = State()
    rename_deck = State()
    add_card_face = State()
    add_card_back = State()
    edit_card = State()

