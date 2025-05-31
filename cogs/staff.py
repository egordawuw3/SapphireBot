import disnake
from disnake.ext import commands
import asyncio
from datetime import datetime
import logging
from utils.embed_utils import make_embed
from utils.permissions import require_staff
from config.constants import BAN_ROLE_ID, MUTE_ROLE_ID, DEFAULT_ROLE_ID, ERROR_COLOR, SUCCESS_COLOR, INFO_COLOR

logger = logging.getLogger(__name__)

class Staff(commands.Cog):
    """Модераторские команды SapphireBot."""
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ban", description="Забанить пользователя с указанием причины")
    @require_staff()
    async def ban(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Причина не указана"):
        """Бан пользователя (выдаёт роль бана, удаляет остальные)."""
        if member.top_role >= inter.author.top_role:
            embed = make_embed(
                title="Ошибка",
                description="Вы не можете забанить участника с равной или более высокой ролью!",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            ban_role = inter.guild.get_role(BAN_ROLE_ID)
            await member.edit(roles=[ban_role], reason=reason)
            embed = make_embed(
                title="Бан пользователя",
                description=f"Пользователь: {member.mention}\nМодератор: {inter.author.mention}\nПричина: {reason}\nДействие: Все роли удалены, выдана роль бана.",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed)
            try:
                dm_embed = make_embed(
                    title="Вы были забанены",
                    description=f"**Сервер:** {inter.guild.name}\n**Причина:** {reason}\nВы потеряли все роли и получили роль бана.",
                    color=ERROR_COLOR
                )
                await member.send(embed=dm_embed)
            except Exception as e:
                logger.warning(f"Не удалось отправить DM о бане: {e}")
        except Exception as e:
            logger.error(f"Ошибка при бане: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось забанить пользователя: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="unban", description="Снять бан с пользователя по ID")
    @require_staff()
    async def unban(self, inter: disnake.ApplicationCommandInteraction, user_id: str = commands.Param(description="ID пользователя для разбана")):
        """Снять бан с пользователя по ID."""
        try:
            member = await inter.guild.fetch_member(int(user_id))
            ban_role = inter.guild.get_role(BAN_ROLE_ID)
            default_role = inter.guild.get_role(DEFAULT_ROLE_ID)
            if ban_role not in member.roles:
                embed = make_embed(
                    title="Ошибка",
                    description="У пользователя нет роли бана!",
                    color=ERROR_COLOR
                )
                await inter.response.send_message(embed=embed, ephemeral=True)
                return
            await member.remove_roles(ban_role, reason="Разбан модератором")
            await member.add_roles(default_role, reason="Восстановление стандартной роли")
            embed = make_embed(
                title="Снятие бана",
                description=f"Пользователь: {member.mention}\nМодератор: {inter.author.mention}\nДействие: Удалена роль бана, выдана стандартная роль.",
                color=SUCCESS_COLOR
            )
            await inter.response.send_message(embed=embed)
        except disnake.NotFound:
            embed = make_embed(
                title="Ошибка",
                description="Пользователь не найден на сервере!",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Ошибка при разбане: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось снять бан: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="mute", description="Замутить пользователя на определенное время")
    @require_staff()
    async def mute(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, duration: int = commands.Param(description="Длительность мута в минутах"), reason: str = "Причина не указана"):
        """Замутить пользователя на определённое время."""
        if member.top_role >= inter.author.top_role:
            embed = make_embed(
                title="Ошибка",
                description="Вы не можете замутить участника с равной или более высокой ролью!",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            mute_role = inter.guild.get_role(MUTE_ROLE_ID)
            if not mute_role:
                raise ValueError("Роль мута не найдена")
            await member.add_roles(mute_role, reason=reason)
            embed = make_embed(
                title="Мут пользователя",
                description=f"Пользователь: {member.mention}\nМодератор: {inter.author.mention}\nДлительность: {duration} минут\nПричина: {reason}\nДействие: Выдана роль мута.",
                color=INFO_COLOR
            )
            await inter.response.send_message(embed=embed)
            await asyncio.sleep(duration * 60)
            if mute_role in member.roles:
                await member.remove_roles(mute_role, reason="Автоматическое снятие мута")
            try:
                dm_embed = make_embed(
                    title="Вы были замучены",
                    description=f"**Сервер:** {inter.guild.name}\n**Длительность:** {duration} минут\n**Причина:** {reason}",
                    color=INFO_COLOR
                )
                await member.send(embed=dm_embed)
            except Exception as e:
                logger.warning(f"Не удалось отправить DM о муте: {e}")
        except Exception as e:
            logger.error(f"Ошибка при муте: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось замутить пользователя: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="unmute", description="Размутить пользователя")
    @require_staff()
    async def unmute(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
        """Размутить пользователя."""
        try:
            mute_role = inter.guild.get_role(MUTE_ROLE_ID)
            if mute_role in member.roles:
                await member.remove_roles(mute_role, reason="Досрочное снятие мута")
            embed = make_embed(
                title="Размут пользователя",
                description=f"Пользователь: {member.mention}\nМодератор: {inter.author.mention}\nДействие: Удалена роль мута.",
                color=SUCCESS_COLOR
            )
            await inter.response.send_message(embed=embed)
            try:
                dm_embed = make_embed(
                    title="Вы были размучены",
                    description=f"**Сервер:** {inter.guild.name}",
                    color=SUCCESS_COLOR
                )
                await member.send(embed=dm_embed)
            except Exception as e:
                logger.warning(f"Не удалось отправить DM о размуте: {e}")
        except Exception as e:
            logger.error(f"Ошибка при размуте: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось размутить пользователя: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(name="clear", description="Очистить сообщения в канале")
    @require_staff()
    async def clear(self, inter: disnake.ApplicationCommandInteraction, amount: int = commands.Param(description="Количество сообщений для удаления", ge=1, le=1000)):
        """Очистить сообщения в канале."""
        try:
            await inter.response.defer(ephemeral=True)
            deleted = await inter.channel.purge(limit=amount)
            embed = make_embed(
                title="Очистка чата",
                description=f"Удалено {len(deleted)} сообщений\nМодератор: {inter.author.mention}\nКанал: {inter.channel.mention}",
                color=SUCCESS_COLOR
            )
            msg = await inter.channel.send(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()
            await inter.edit_original_message(
                embed=make_embed(
                    title="Успех",
                    description=f"Успешно удалено {len(deleted)} сообщений",
                    color=SUCCESS_COLOR
                )
            )
        except Exception as e:
            logger.error(f"Ошибка при очистке чата: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось очистить сообщения: {e}",
                color=ERROR_COLOR
            )
            await inter.edit_original_message(embed=embed)

    @commands.slash_command(name="kick", description="Выгнать пользователя с сервера")
    @require_staff()
    async def kick(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Причина не указана"):
        """Выгнать пользователя с сервера."""
        if member.top_role >= inter.author.top_role:
            embed = make_embed(
                title="Ошибка",
                description="Вы не можете выгнать участника с равной или более высокой ролью!",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            await member.kick(reason=reason)
            embed = make_embed(
                title="Кик пользователя",
                description=f"Пользователь: {member.mention}\nМодератор: {inter.author.mention}\nПричина: {reason}",
                color=INFO_COLOR
            )
            await inter.response.send_message(embed=embed)
            try:
                dm_embed = make_embed(
                    title="Вы были кикнуты",
                    description=f"**Сервер:** {inter.guild.name}\n**Причина:** {reason}",
                    color=INFO_COLOR
                )
                await member.send(embed=dm_embed)
            except Exception as e:
                logger.warning(f"Не удалось отправить DM о кике: {e}")
        except Exception as e:
            logger.error(f"Ошибка при кике: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось выгнать пользователя: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Staff(bot))