from telebot.util import quick_markup

menu_markup = quick_markup(
    {
        'Мои колоды': {'callback_data': 'show_decks'},
        'Премиум-доступ': {'callback_data': '/2'},

    },
    row_width=1
)

no_decks_markup = quick_markup(
    {
        'Создать колоду': {'callback_data': 'create_deck'},
        'Демо': {'callback_data': 'demo'},

    },
    row_width=1
)

deck_menu_markup = quick_markup(
    {
        'Повторять карточки': {'callback_data': 'learn'},
        'Изменить тип колоды': {'callback_data': 'change_deck_type'},
        'Добавить карточку': {'callback_data': 'add_card'},
        'Удалить колоду': {'callback_data': 'delete_deck'}
    }
)

card_add_markup = quick_markup(
    {
        'Добавить еще карточку': {'callback_data': 'add_card'},
        'Вернуться в меню': {'callback_data': 'show_menu'}
    }
)