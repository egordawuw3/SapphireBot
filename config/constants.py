# ID ролей для разных уровней
ROLE_LEVELS = {
    1: 1364889084098510868,
    5: 1364889174280372274,
    10: 1364889171222855760,
    15: 1364889168592769104,
    25: 1364889165333925968,
    35: 1364889161886204054,
    45: 1364889851949879339,
    50: 1364889574639407116
}

# Цвета для разных уровней
LEVEL_COLORS = {
    40: 0xFF0000,  # Красный
    30: 0xFFA500,  # Оранжевый
    20: 0xFFFF00,  # Желтый
    10: 0x00FF00,  # Зеленый
    0: 0x0000FF    # Синий
}

# Эмодзи для разных уровней
LEVEL_EMOJIS = {
    40: "🌟",
    30: "💎",
    20: "🔮",
    10: "⭐",
    0: "✨"
}
EMOJI_GOLD = "🥇"
EMOJI_SILVER = "🥈"
EMOJI_BRONZE = "🥉"

# Настройки для системы уровней
XP_PER_MESSAGE = 5  # Убедитесь, что значение равно 5
BASE_XP = 100
MAX_LEVEL = 50
XP_COOLDOWN = 0  # Полное отключение кулдауна

# Настройки для музыкального плеера
MAX_SONG_DURATION = 600  # Максимальная длительность песни в секундах (10 минут)

# Настройки для AI чата
AI_SESSION_TIMEOUT = 3600  # Время жизни сессии в секундах (1 час)
AI_MAX_HISTORY = 20  # Максимальное количество сообщений в истории

# Константы для SapphireBot

STAFF_ROLE_ID = 1207281299849744385
BAN_ROLE_ID = 1222507607026307082
DEFAULT_ROLE_ID = 832314278702874694
MUTE_ROLE_ID = 999728904166187018

DEFAULT_COLOR = 0x2B65EC
ERROR_COLOR = 0xFF0000
SUCCESS_COLOR = 0x00FF00
WARNING_COLOR = 0xFF9900
INFO_COLOR = 0x3498db

FOOTER_TEXT = "С уважением, администрация Sapphire Creators 💎"

# Эмодзи (пример)
EMOJI_SAPPHIRE = "<:Sapphire_icon:1159784599010938922>"
EMOJI_BAN = "🔨"
EMOJI_MUTE = "🔇"
EMOJI_KICK = "👢"
EMOJI_CLEAR = "🧹"

import disnake

EMBED_COLOR = disnake.Color.blurple()

INFO_BANNER_CHANNEL_ID = 1380248699250282506
INFO_BANNER_URL = "https://cdn.discordapp.com/attachments/998671608652759081/1380259763824234526/3cef6b99-0416-4ae7-9068-4f3a46a655bb.png?ex=68433a93&is=6841e913&hm=5948fb60ddc0e1b99cac6a47d0ba9d9b364873a57df5ec62bc2b14879429d0da&"
EMOJI_LOGO_SAPPHIRE = "<:logosapphire:1369745518418198778>"
EMOJI_SAPPHIRE_ICON = "<:Sapphire_icon:1159787682734542869>"
EMOJI_SAPPHIRE_ICON2 = "<:Sapphire_icon:1159784251751940107>"
EMOJI_SAPPHIRE_ICON3 = "<:Sapphire_icon:1151957227855413338>"
EMOJI_SAPPHIRE_ICON4 = "<:Sapphire_icon:1159787647712120924>"
ECONOMY_ROLE_ID = 1380255011149316148
HELP_CHANNEL_ID = 998671608652759081
CREATORS_CHANNEL_ID = 1362137776027340990
QUESTS_CHANNEL_ID = 902640230018973746