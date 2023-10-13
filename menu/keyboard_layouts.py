from telebot.util import quick_markup

menu_markup = quick_markup(
    {
        'Мои колоды': {'callback_data': 'show_decks'},
        'Премиум-доступ': {'callback_data': '/2'},

    },
    row_width=1
)
first_login_markup = quick_markup(
    {
        'Создать колоду': {'callback_data': 'create_deck'},
        'Демо': {'callback_data': 'demo'},

    },
    row_width=1
)
