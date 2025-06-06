import disnake
from disnake.ext import commands
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR

logger = logging.getLogger(__name__)

# --- Ticket Modal для разных типов ---
class CustomTicketModal(disnake.ui.Modal):
    def __init__(self, ticket_type: str, title: str, label: str):
        self.ticket_type = ticket_type
        components = [
            disnake.ui.TextInput(
                label=label,
                custom_id="ticket_reason",
                style=disnake.TextInputStyle.paragraph
            )
        ]
        super().__init__(
            title=title,
            custom_id=f"modal_{ticket_type}",
            components=components
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        await inter.response.defer(ephemeral=True)
        guild = inter.guild
        ticket_number = await self.get_next_ticket_number(guild)
        overwrites = {
            guild.default_role: disnake.PermissionOverwrite(read_messages=False),
            inter.user: disnake.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: disnake.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        category = disnake.utils.get(guild.categories, name="— × tickets")
        if not category:
            category = await guild.create_category("— × tickets", overwrites=overwrites)
        channel = await guild.create_text_channel(
            name=f"ticket-{ticket_number}",
            category=category,
            overwrites=overwrites,
            topic=f"Создатель: {inter.user.id} | Тип: {self.ticket_type}"
        )
        type_map = {
            "deposit": "Покупка валюты за деньги (донат)",
            "exchange": "Покупка услуг за валюту",
            "tasks": "Покупка валюты за услуги"
        }
        fields = [
            {"name": "Создатель", "value": inter.user.mention, "inline": True},
            {"name": "Тип заявки", "value": type_map.get(self.ticket_type, self.ticket_type), "inline": True},
            {"name": "Причина", "value": inter.text_values["ticket_reason"], "inline": False}
        ]
        embed = make_embed(
            title=f"Тикет #{ticket_number}",
            description=f"🎫 {type_map.get(self.ticket_type, self.ticket_type)}",
            color=INFO_COLOR,
            fields=fields
        )
        await channel.send(embed=embed)
        await inter.followup.send(f"Тикет создан в канале {channel.mention}", ephemeral=True)

    async def get_next_ticket_number(self, guild: disnake.Guild) -> int:
        existing = [c for c in guild.text_channels if c.name.startswith("ticket-")]
        numbers = [int(c.name.split("-", 1)[1]) for c in existing if c.name.split("-", 1)[1].isdigit()]
        return max(numbers, default=0) + 1

# --- View с кнопками ---
class TicketButtons(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(label="Deposit", style=disnake.ButtonStyle.green, emoji="💸", custom_id="ticket_deposit")
    async def deposit(self, button, inter):
        modal = CustomTicketModal("deposit", "Покупка валюты за деньги", "Опишите, сколько и какую валюту хотите купить")
        await inter.response.send_modal(modal)

    @disnake.ui.button(label="Exchange", style=disnake.ButtonStyle.blurple, emoji="🔄", custom_id="ticket_exchange")
    async def exchange(self, button, inter):
        modal = CustomTicketModal("exchange", "Покупка услуг за валюту", "Опишите, какую услугу и за сколько SC хотите купить")
        await inter.response.send_modal(modal)

    @disnake.ui.button(label="Tasks", style=disnake.ButtonStyle.gray, emoji="📝", custom_id="ticket_tasks")
    async def tasks(self, button, inter):
        modal = CustomTicketModal("tasks", "Покупка валюты за услуги", "Опишите, какую услугу вы готовы выполнить и за сколько SC")
        await inter.response.send_modal(modal)

class BotInfo(commands.Cog):
    """Cog для автоматического сообщения о Sapphire Bot и его использовании."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1380248699250282506

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            logger.error("❌ Канал для информации о боте не найден!")
            return
        await channel.purge()
        banner_embed = make_embed(
            title=" ",
            color=INFO_COLOR
        )
        banner_embed.set_image(url="https://cdn.discordapp.com/attachments/998671608652759081/1380589388282462280/4747a6e4-a2d0-47ca-be3f-8d7fefc10f2a.png?ex=68446d90&is=68431c10&hm=8c3ee836fc453e4f9adbe1687c3b2d3a709f5665f42c4abced97caea960bc347&")
        await channel.send(embed=banner_embed)
        main_embed = make_embed(
            title="Информация о Sapphire Bot",
            description=(
                "> <:logosapphire:1369745518418198778> Здесь собрана вся важная информация о Sapphire Bot и том, как им пользоваться.\n"
                "> ‎\n"
                "> — Основные функции\n"
                "> Чтобы узнать всевозможные команды бота, используйте команду /help в <#998671608652759081>\n"
                "> ‎\n"
                "> — Экономика\n"
                "> 1. О валюте сервера\n"
                "> <:Sapphire_icon:1159787682734542869> Sapphire Coin (SC) — это внутренняя валюта нашего Discord-сервера, созданная для поощрения активности и вовлечённости участников. Её можно обменять на реальные услуги команды: дизайн, монтаж, программирование, рекламу и даже на РЕАЛЬНЫЕ ДЕНЬГИ! Sapphire Coin — ваша ценность в экосистеме сервера.\n"
                "> 2. На что можно обменять?\n"
                "> <:Sapphire_icon:1159784251751940107> Ниже приведен перечень доступных товаров и услуг, на которые можно обменять Сапфир коины:\n"
                "> - Фиат: - 1₴ - 10SC; 1₽ = 5SC; 1₮ = 410SC; 1zł = 100SC; 1€ = 460SC (Вывод средств осуществляется исключительно в указанных фиатных валютах).\n"
                "> - Услуги Sapphire Creators из <#1362137776027340990> - дизайн, монтаж и.т.п. (Сумма конвертируется в SC по указанному выше курсу)\n"
                "> - Роль <@&1380255011149316148>, которая даёт +10% к заработку на 30 дней - 2750SC\n"
                "> - Отдельный текстовый / голосовой канал лично для вас - 1500SC\n"
                "> 3. Как получить?\n"
                "> <:Sapphire_icon:1151957227855413338> Используйте команду /bal & /scoreboard для анализа своего баланса и перечень способов по заработку коинов:\n"
                "> - Бампы сервера - используйте команды /bump в <#998671608652759081>, за одну команду вам начисляется 1SC\n"
                "> - Войсы - 1 час активности в голосовых каналах (микрофон должен быть включён) = 20SC\n"
                "> - Приглашение друзей - Пригласите друга, который активит больше 3 дней = 100SC (лимит: 3 друга в 24h)\n"
                "> - Специальные задания - Выполняйте особые задания от стафа = от 50SC до 200SC (см.<#902640230018973746>)\n"
                "> - Донат - 100₴ - 800SC; 100₽ = 400SC; 10₮ = 4000SC; 100zł = 9000SC; 10€ = 4500SC (Вывод средств осуществляется исключительно в указанных фиатных валютах)\n"
                "> - Зарплата для стафа - вступайте в ряды персоналы и получайте минимальный оклад (от 800SC в неделю)\n"
                "> ‎\n"
                "> <:Sapphire_icon:1159787647712120924> ВАЖНО: коины начисляются раз в 24 часа администрацией."
            ),
            color=INFO_COLOR
        )
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif")
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        await channel.send(embed=main_embed)

        # Новое сообщение с кнопками и ссылкой
        info_embed = make_embed(
            description=(
                "<:Sapphire_icon:1159785545694711839> Используйте ниже кнопки, чтобы:\n"
                "> ‎\n"
                "> Купить валюту за деньги\n"
                "> Купить услуги за валюту\n"
                "> Получить валюту за выполнение специальных заданий \n"
                "> ‎\n"
                "> <:Sapphire_icon:1159787682734542869> Остались вопросы? [Нажмите сюда](https://discord.com/channels/832291503581167636/1054101394270978119)."
            ),
            color=INFO_COLOR
        )
        info_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        await channel.send(embed=info_embed, view=TicketButtons())

def setup(bot: commands.Bot) -> None:
    bot.add_cog(BotInfo(bot)) 