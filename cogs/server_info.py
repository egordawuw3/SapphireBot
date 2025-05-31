import disnake
from disnake.ext import commands
from datetime import datetime, timezone
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR, ERROR_COLOR

logger = logging.getLogger(__name__)

class ServerInfo(commands.Cog):
    """Команда информации о сервере."""
    def __init__(self, bot):
        self.bot = bot

    def format_time_ago(self, delta_days: int) -> str:
        years = delta_days // 365
        months = (delta_days % 365) // 30
        if years == 0:
            if months == 0:
                return "менее месяца назад"
            else:
                return f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'} назад"
        else:
            year_text = f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}"
            if months == 0:
                return f"{year_text} назад"
            else:
                month_text = f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}"
                return f"{year_text} и {month_text} назад"

    @commands.slash_command(
        name="serverinfo",
        description="Показывает информацию о сервере"
    )
    async def server_info(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Показывает информацию о сервере."""
        try:
            guild = inter.guild
            total_members = len(guild.members)
            humans = len([m for m in guild.members if not m.bot])
            bots = len([m for m in guild.members if m.bot])
            online = len([m for m in guild.members if str(m.status) == "online"])
            idle = len([m for m in guild.members if str(m.status) == "idle"])
            dnd = len([m for m in guild.members if str(m.status) == "dnd"])
            offline = len([m for m in guild.members if str(m.status) == "offline"])
            total_channels = len(guild.channels)
            text_channels = len(guild.text_channels)
            voice_channels = len(guild.voice_channels)
            forum_channels = len([c for c in guild.channels if isinstance(c, disnake.ForumChannel)])
            announcement_channels = len([c for c in guild.channels if isinstance(c, disnake.TextChannel) and c.is_news()])
            created_days = (datetime.now(timezone.utc) - guild.created_at).days
            fields = [
                {
                    "name": "Участники:",
                    "value": f"👥 Всего: {total_members}\n👤 Людей: {humans}\n🤖 Ботов: {bots}",
                    "inline": True
                },
                {
                    "name": "По статусам:",
                    "value": f"🟢 В сети: {online}\n🌙 Неактивен: {idle}\n⛔ Не беспокоить: {dnd}\n⚪ Не в сети: {offline}",
                    "inline": True
                },
                {
                    "name": "Каналы:",
                    "value": f"💬 Всего: {total_channels}\n# Текстовых: {text_channels}\n💭 Форумов: {forum_channels}\n🔊 Голосовых: {voice_channels}\n📢 Объявления: {announcement_channels}",
                    "inline": True
                },
                {
                    "name": "Владелец:",
                    "value": f"{guild.owner.name}",
                    "inline": True
                },
                {
                    "name": "Уровень проверки:",
                    "value": f"{str(guild.verification_level).capitalize()}",
                    "inline": True
                },
                {
                    "name": "Дата создания:",
                    "value": f"{guild.created_at.strftime('%d %B %Y г.')}\n{self.format_time_ago(created_days)}",
                    "inline": True
                }
            ]
            embed = make_embed(
                title=f"Информация о сервере {guild.name}",
                color=INFO_COLOR,
                fields=fields,
                thumbnail=guild.icon.url if guild.icon else None
            )
            await inter.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка в server_info: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось получить информацию о сервере: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(ServerInfo(bot))