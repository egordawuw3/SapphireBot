import disnake
from disnake.ext import commands
import math
import logging
from datetime import datetime, timedelta, timezone
from utils.embed_utils import make_embed
from config.constants import ROLE_LEVELS, LEVEL_COLORS, LEVEL_EMOJIS, XP_PER_MESSAGE, BASE_XP, MAX_LEVEL, XP_COOLDOWN, INFO_COLOR, ERROR_COLOR, SUCCESS_COLOR

logger = logging.getLogger(__name__)

class Levels(commands.Cog):
    """Система уровней и опыта."""
    def __init__(self, bot):
        self.bot = bot
        from utils.database import Database
        self.db = Database()
        self.xp_per_message = XP_PER_MESSAGE
        self.base_xp = BASE_XP
        self.max_level = MAX_LEVEL
        self.xp_cooldown = XP_COOLDOWN
        self.user_cooldowns = {}

    async def update_roles(self, member: disnake.Member, level: int) -> None:
        """Обновляет роли пользователя в зависимости от уровня."""
        try:
            max_applicable_level = max((req_level for req_level in ROLE_LEVELS if level >= req_level), default=None)
            if max_applicable_level is None:
                return
            target_role_id = ROLE_LEVELS[max_applicable_level]
            target_role = member.guild.get_role(target_role_id)
            if not target_role:
                logger.error(f"Роль для уровня {max_applicable_level} не найдена")
                return
            level_roles = [member.guild.get_role(role_id) for role_id in ROLE_LEVELS.values() if member.guild.get_role(role_id)]
            roles_to_remove = [r for r in member.roles if r in level_roles and r != target_role]
            if target_role not in member.roles:
                await member.add_roles(target_role)
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            # Сообщение о новых ролях (опционально)
        except Exception as e:
            logger.error(f"Ошибка при обновлении ролей: {e}")

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message) -> None:
        if message.author.bot:
            return
        if message.channel.name.lower().find('spam') != -1:
            return
        user_id = str(message.author.id)
        current_time = datetime.now()
        if user_id in self.user_cooldowns:
            time_diff = (current_time - self.user_cooldowns[user_id]).total_seconds()
            if time_diff < self.xp_cooldown:
                return
        self.user_cooldowns[user_id] = current_time
        user_data = self.db.get_user_data(user_id)
        old_level = user_data["level"]
        user_data["xp"] += self.xp_per_message
        new_level = self.calculate_level(user_data["xp"])
        user_data["level"] = new_level
        self.db.update_user_data(user_id, user_data["xp"], user_data["level"])
        if new_level > old_level:
            try:
                await self.update_roles(message.author, new_level)
            except Exception as e:
                logger.error(f"Ошибка при обновлении ролей после повышения уровня: {e}")

    @commands.slash_command(name="rank", description="Показать уровень и опыт участника")
    async def rank(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = commands.Param(default=None, description="Участник для проверки (оставьте пустым для своего ранга)")) -> None:
        """Показать уровень и опыт участника."""
        try:
            target = member or inter.author
            user_id = str(target.id)
            user_data = self.db.get_user_data(user_id)
            current_xp = user_data["xp"]
            current_level = user_data["level"]
            xp_for_next = self.calculate_xp_for_next_level(current_level)
            color = self.get_level_color(current_level)
            emoji = self.get_level_emoji(current_level)
            fields = [
                {"name": "Уровень", "value": f"{emoji} {current_level}", "inline": True},
                {"name": "Опыт", "value": f"{current_xp} XP", "inline": True},
                {"name": "До следующего уровня", "value": f"{xp_for_next - current_xp if xp_for_next != float('inf') else 'MAX'} XP", "inline": True}
            ]
            embed = make_embed(
                title=f"Ранг {target.display_name}",
                color=color,
                fields=fields,
                thumbnail=target.display_avatar.url
            )
            await inter.response.send_message(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка в rank: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось получить ранг: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="leaderboard", description="Показать таблицу лидеров")
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Показать таблицу лидеров."""
        try:
            await inter.response.defer()
            top_users = self.db.get_top_users(10)
            user_objects = {}
            for user_data in top_users:
                try:
                    user_id = int(user_data["user_id"])
                    user = await self.bot.get_or_fetch_user(user_id)
                    if user:
                        user_objects[user_data["user_id"]] = user
                except Exception as e:
                    logger.error(f"Ошибка при получении пользователя {user_data['user_id']}: {e}")
            desc = ""
            for idx, user_data in enumerate(top_users, 1):
                user = user_objects.get(user_data["user_id"])
                name = user.display_name if user else f"ID {user_data['user_id']}"
                desc += f"**{idx}. {name}** — {user_data['level']} lvl, {user_data['xp']} XP\n"
            embed = make_embed(
                title="Таблица лидеров",
                description=desc or "Нет данных.",
                color=INFO_COLOR
            )
            await inter.followup.send(embed=embed)
        except Exception as e:
            logger.error(f"Ошибка в leaderboard: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось получить таблицу лидеров: {e}",
                color=ERROR_COLOR
            )
            await inter.followup.send(embed=embed, ephemeral=True)

    def calculate_level(self, xp: int) -> int:
        """Вычисляет уровень на основе количества XP."""
        if xp < self.base_xp:
            return 0
        return min(int(math.log(xp / self.base_xp, 1.5) + 1), self.max_level)

    def calculate_xp_for_next_level(self, current_level: int) -> int:
        """Вычисляет количество XP, необходимое для следующего уровня."""
        if current_level >= self.max_level:
            return float('inf')
        return int(self.base_xp * (1.5 ** (current_level)))

    def get_level_emoji(self, level: int) -> str:
        """Возвращает эмодзи в зависимости от уровня."""
        for min_level, emoji in sorted(LEVEL_EMOJIS.items(), reverse=True):
            if level >= min_level:
                return emoji
        return "✨"

    def get_level_color(self, level: int) -> int:
        """Возвращает цвет в зависимости от уровня."""
        for min_level, color in sorted(LEVEL_COLORS.items(), reverse=True):
            if level >= min_level:
                return color
        return INFO_COLOR

def setup(bot):
    bot.add_cog(Levels(bot))