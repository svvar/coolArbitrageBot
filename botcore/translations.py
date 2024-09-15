translations = {
    'ua':
        {
            'menu_check_accs': 'Перевірити акаунти на блокування',
            'menu_2fa': '2fa код',
            'menu_tiktok': 'Завантажити відео з TikTok',
            'menu_apps': 'Додатки Google Play',

            'start_msg': 'Привіт, я бот для арбітражу',

            'accs_ask_list': 'Відправте список посилань на акаунти або txt файл з посиланнями',
            'accs_info_msg': '*Активних: {}\nЗаблокованих: {}\nПомилок перевірки: {}*',
            'accs_active_label': 'Активні акаунти',
            'accs_banned_label': 'Заблоковані акаунти',


            '2fa_select_key': 'Введіть ключ для 2fa або виберіть з нещодавніх:',
            '2fa_enter_key': 'Введіть ключ для 2fa:',
            '2fa_wrong_key': 'Неправильний ключ',
            '2fa_code_msg': 'Ваш код: `{}` \nТермін дії: {} секунд',

            'tiktok_ask_url': 'Відправте посилання на відео з TikTok',
            'tiktok_not_found': 'Відео не знайдено',

            'apps_add_button': 'Додати додаток',
            'apps_delete_button': 'Видалити додаток',
            'apps_no_apps': 'У вас немає додатків',
            'apps_ask_url': 'Введіть посилання на додаток в Google Play',
            'apps_bad_url': 'Непідохдяще посилання, введіть посилання на додаток в Google Play',
            'apps_already_blocked': 'Ви намагаєтесь додати вже заблокований додаток або такого не існувало',
            'apps_added_yet': 'Додаток вже додано',
            'apps_add_success': 'Додаток *{}* успішно додано',
            'apps_choose_delete': 'Виберіть додаток для видалення:',
            'apps_delete_success': 'Додаток *{}* видалено',
            'apps_blocked_warning': '🚨 УВАГА! Ваш додаток *{}* заблоковано'


        },
    'ru':
        {
            'menu_check_accs': 'Проверить аккаунты на блокировки',
            'menu_2fa': '2fa код',
            'menu_tiktok': 'Загрузить видео с TikTok',
            'menu_apps': 'Приложения Google Play',

            'start_msg': 'Привет, я бот для арбитража',

            'accs_ask_list': 'Отправьте список ссылок на аккаунты или txt файл с ссылками',
            'accs_info_msg': '*Активных: {}\nЗаблокированных: {}\nОшибок проверки: {}*',
            'accs_active_label': 'Активные аккаунты',
            'accs_banned_label': 'Заблокированные аккаунты',

            '2fa_select_key': 'Введите ключ для 2fa или выберите из недавних:',
            '2fa_enter_key': 'Введите ключ для 2fa:',
            '2fa_wrong_key': 'Неправильный ключ',
            '2fa_code_msg': 'Ваш код: `{}` \nСрок действия: {} секунд',

            'tiktok_ask_url': 'Отправьте ссылку на видео с TikTok',
            'tiktok_not_found': 'Видео не найдено',

            'apps_add_button': 'Добавить приложение',
            'apps_delete_button': 'Удалить приложение',
            'apps_no_apps': 'У вас нет приложений',
            'apps_ask_url': 'Введите ссылку на приложение в Google Play',
            'apps_bad_url': 'Неподходящая ссылка, введите ссылку на приложение в Google Play',
            'apps_already_blocked': 'Вы пытаетесь добавить уже заблокированное приложение или такого не существовало',
            'apps_added_yet': 'Приложение уже добавлено',
            'apps_add_success': 'Приложение *{}* успешно добавлено',
            'apps_choose_delete': 'Выберите приложение для удаления:',
            'apps_delete_success': 'Приложение *{}* удалено',
            'apps_blocked_warning': '🚨 ВНИМАНИЕ! Ваше приложение *{}* заблокировано'
        }
}


def handlers_variants(key_string):
    possible_translations = []
    for key, value in translations.items():
        if key_string in value:
            possible_translations.append(value[key_string].lower())

    return possible_translations

