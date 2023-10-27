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
        'Добавить карточку': {'callback_data': 'add_card'},
        'Удалить': {'callback_data': 'delete_deck'},
        'Переименовать': {'callback_data': 'rename_deck'},
        'Вернуться в меню': {'callback_data': 'show_menu'}
    },
    row_width=1
)

card_add_markup = quick_markup(
    {
        'Добавить еще карточку': {'callback_data': 'add_card'},
        'Вернуться в меню': {'callback_data': 'show_menu'}
    }
)

learn_mode_markup = quick_markup(
    {
        'Все карточки': {'callback_data': 'learn_mode:all'},
        'Новые карточки': {'callback_data': 'learn_mode:new'},
        'По расписанию': {'callback_data': 'learn_mode:schedule'}
    }
)


deck_mode_markup = quick_markup(
    {
        'Сначала лицо': {'callback_data': 'deck_mode:face'},
        'Сначала оборот': {'callback_data': 'deck_mode:back'},
        'Случайно': {'callback_data': 'deck_mode:random'}
    }
)

card_markup = quick_markup(
    {
        'Завтра': {'callback_data': 'repeat_tomorrow'},
        'Через неделю': {'callback_data': 'repeat_week'},
        'Через месяц': {'callback_data': 'repeat_month'},
        'Повторить еще': {'callback_data': 'repeat_now'},
        'Удалить карточку': {'callback_data': 'delete_card'},
        'Вернуться в меню': {'callback_data': 'show_menu'}
    }
)

empty_deck_markup = quick_markup(
    {
        'Вернуться в меню': {'callback_data': 'show_menu'}
    }
)


