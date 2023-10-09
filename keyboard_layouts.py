from telebot.util import quick_markup

menu_markup = quick_markup(
    {
        'Мои колоды': {'callback_data': '/1'},
        'Премиум-доступ': {'callback_data': '/2'},

    },
    row_width=3
)

