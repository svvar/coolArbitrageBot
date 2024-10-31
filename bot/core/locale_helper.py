import gettext

from babel import Locale

countries = {
    'uk':{
        'az_AZ': '🇦🇿 Азербайджан', 'bg_BG': '🇧🇬 Болгарія', 'cs_CZ': '🇨🇿 Чехія', 'da_DK': '🇩🇰 Данія', 'de_AT': '🇦🇹 Австрія',
        'de_CH': '🇨🇭 Швейцарія', 'de_DE': '🇩🇪 Німеччина', 'el_GR': '🇬🇷 Греція', 'en_AU': '🇦🇺 Австралія',
        'en_GB': '🇬🇧 Великобританія', 'en_US': '🇺🇸 США', 'en_PH': '🇵🇭 Філіппіни', 'es_ES': '🇪🇸 Іспанія', 'es_MX': '🇲🇽 Мексика',
        'es_CL': '🇨🇱 Чилі', 'et_EE': '🇪🇪 Естонія', 'fi_FI': '🇫🇮 Фінляндія', 'fr_FR': '🇫🇷 Франція', 'he_IL': '🇮🇱 Ізраїль',
        'hi_IN': '🇮🇳 Індія', 'hr_HR': '🇭🇷 Хорватія', 'hu_HU': '🇭🇺 Угорщина', 'hy_AM': '🇦🇲 Вірменія', 'id_ID': '🇮🇩 Індонезія',
        'it_IT': '🇮🇹 Італія', 'ja_JP': '🇯🇵 Японія', 'ko_KR': '🇰🇷 Південна Корея', 'lt_LT': '🇱🇹 Литва', 'lv_LV': '🇱🇻 Латвія',
        'nl_NL': '🇳🇱 Нідерланди', 'pl_PL': '🇵🇱 Польща', 'pt_BR': '🇧🇷 Бразилія', 'pt_PT': '🇵🇹 Португалія', 'ro_RO': '🇷🇴 Румунія',
        'ru_RU': '🇷🇺 Росія', 'sk_SK': '🇸🇰 Словаччина', 'sl_SI': '🇸🇮 Словенія', 'sv_SE': '🇸🇪 Швеція', 'tr_TR': '🇹🇷 Туреччина',
        'uk_UA': '🇺🇦 Україна'
    },
    'ru':{
        'az_AZ': '🇦🇿 Азербайджан', 'bg_BG': '🇧🇬 Болгария', 'cs_CZ': '🇨🇿 Чехия', 'da_DK': '🇩🇰 Дания', 'de_AT': '🇦🇹 Австрия',
        'de_CH': '🇨🇭 Швейцария', 'de_DE': '🇩🇪 Германия', 'el_GR': '🇬🇷 Греция', 'en_AU': '🇦🇺 Австралия',
        'en_GB': '🇬🇧 Великобритания', 'en_US': '🇺🇸 США', 'en_PH': '🇵🇭 Филиппины', 'es_ES': '🇪🇸 Испания', 'es_MX': '🇲🇽 Мексика',
        'es_CL': '🇨🇱 Чили', 'et_EE': '🇪🇪 Эстония', 'fi_FI': '🇫🇮 Финляндия', 'fr_FR': '🇫🇷 Франция', 'he_IL': '🇮🇱 Израиль',
        'hi_IN': '🇮🇳 Индия', 'hr_HR': '🇭🇷 Хорватия', 'hu_HU': '🇭🇺 Венгрия', 'hy_AM': '🇦🇲 Армения', 'id_ID': '🇮🇩 Индонезия',
        'it_IT': '🇮🇹 Италия', 'ja_JP': '🇯🇵 Япония', 'ko_KR': '🇰🇷 Южная Корея', 'lt_LT': '🇱🇹 Литва', 'lv_LV': '🇱🇻 Латвия',
        'nl_NL': '🇳🇱 Нидерланды', 'pl_PL': '🇵🇱 Польша', 'pt_BR': '🇧🇷 Бразилия', 'pt_PT': '🇵🇹 Португалия', 'ro_RO': '🇷🇴 Румыния',
        'ru_RU': '🇷🇺 Россия', 'sk_SK': '🇸🇰 Словакия', 'sl_SI': '🇸🇮 Словения', 'sv_SE': '🇸🇪 Швеция', 'tr_TR': '🇹🇷 Турция',
        'uk_UA': '🇺🇦 Украина'

    },
    'en':{
        'az_AZ': '🇦🇿 Azerbaijan', 'bg_BG': '🇧🇬 Bulgaria', 'cs_CZ': '🇨🇿 Czech Republic', 'da_DK': '🇩🇰 Denmark', 'de_AT': '🇦🇹 Austria',
        'de_CH': '🇨🇭 Switzerland', 'de_DE': '🇩🇪 Germany', 'el_GR': '🇬🇷 Greece', 'en_AU': '🇦🇺 Australia',
        'en_GB': '🇬🇧 United Kingdom', 'en_US': '🇺🇸 United States', 'en_PH': '🇵🇭 Philippines', 'es_ES': '🇪🇸 Spain', 'es_MX': '🇲🇽 Mexico',
        'es_CL': '🇨🇱 Chile', 'et_EE': '🇪🇪 Estonia', 'fi_FI': '🇫🇮 Finland', 'fr_FR': '🇫🇷 France', 'he_IL': '🇮🇱 Israel',
        'hi_IN': '🇮🇳 India', 'hr_HR': '🇭🇷 Croatia', 'hu_HU': '🇭🇺 Hungary', 'hy_AM': '🇦🇲 Armenia', 'id_ID': '🇮🇩 Indonesia',
        'it_IT': '🇮🇹 Italy', 'ja_JP': '🇯🇵 Japan', 'ko_KR': '🇰🇷 South Korea', 'lt_LT': '🇱🇹 Lithuania', 'lv_LV': '🇱🇻 Latvia',
        'nl_NL': '🇳🇱 Netherlands', 'pl_PL': '🇵🇱 Poland', 'pt_BR': '🇧🇷 Brazil', 'pt_PT': '🇵🇹 Portugal', 'ro_RO': '🇷🇴 Romania',
        'ru_RU': '🇷🇺 Russia', 'sk_SK': '🇸🇰 Slovakia', 'sl_SI': '🇸🇮 Slovenia', 'sv_SE': '🇸🇪 Sweden', 'tr_TR': '🇹🇷 Turkey',
        'uk_UA': '🇺🇦 Ukraine'


    }
}
locales = {
    'az_AZ': 'Azerbaijan',
    'bg_BG': 'Bulgaria',
    'cs_CZ': 'Czech Republic',
    'da_DK': 'Denmark',
    'de_AT': 'Austria',
    'de_CH': 'Switzerland',
    'de_DE': 'Germany',
    'el_GR': 'Greece',
    'en_AU': 'Australia',
    'en_GB': 'United Kingdom',
    'en_US': 'United States',
    'en_PH': 'Philippines',
    'es_ES': 'Spain',
    'es_MX': 'Mexico',
    'es_CL': 'Chile',
    'et_EE': 'Estonia',
    'fi_FI': 'Finland',
    'fr_FR': 'France',
    'he_IL': 'Israel',
    'hi_IN': 'India',
    'hr_HR': 'Croatia',
    'hu_HU': 'Hungary',
    'hy_AM': 'Armenia',
    'id_ID': 'Indonesia',
    'it_IT': 'Italy',
    'ja_JP': 'Japan',
    'ko_KR': 'South Korea',
    'lt_LT': 'Lithuania',
    'lv_LV': 'Latvia',
    'nl_NL': 'Netherlands',
    'pl_PL': 'Poland',
    'pt_BR': 'Brazil',
    'pt_PT': 'Portugal',
    'ro_RO': 'Romania',
    'ru_RU': 'Russia',
    'sk_SK': 'Slovakia',
    'sl_SI': 'Slovenia',
    'sv_SE': 'Sweden',
    'tr_TR': 'Turkey',
    'uk_UA': 'Ukraine',
}

def translate_string(locale_name, message_original):
    user_locale = Locale.parse(locale_name)

    translations = gettext.translation(
        domain='messages',
        localedir='locales',
        languages=[str(user_locale)]
    )

    _ = translations.gettext

    translated_message = _(message_original)
    return translated_message
