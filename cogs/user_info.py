import disnake
from disnake.ext import commands
from datetime import datetime, timezone
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR, ERROR_COLOR

logger = logging.getLogger(__name__)

class UserInfo(commands.Cog):
    """Команда информации о пользователе."""
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
        name="user",
        description="Показывает информацию о пользователе"
    )
    async def user_info(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        """Показывает информацию о пользователе или о себе."""
        try:
            member = member or inter.author
            now = datetime.now(timezone.utc)
            joined_days = (now - member.joined_at).days
            created_days = (now - member.created_at).days
            fields = [
                {
                    "name": "Основная информация",
                    "value": (
                        f"**Имя пользователя:** {member.name} ({member.display_name})\n"
                        f"**Статус:** {str(member.status).title()}\n"
                        f"**Присоединился:** {member.joined_at.strftime('%d %B %Y г.')} ({self.format_time_ago(joined_days)})\n"
                        f"**Дата регистрации:** {member.created_at.strftime('%d %B %Y г.')} ({self.format_time_ago(created_days)})\n"
                        f"**ID:** {member.id}"
                    ),
                    "inline": False
                }
            ]
            embed = make_embed(
                title=f"Информация о {member.display_name}",
                color=INFO_COLOR,
                fields=fields,
                thumbnail=member.display_avatar.url
            )
            await inter.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка в user_info: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось получить информацию о пользователе: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(UserInfo(bot))