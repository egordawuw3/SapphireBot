import disnake
from disnake.ext import commands
from utils.embed_utils import make_embed
from utils.economy_service import EconomyService
from utils.permissions import require_staff
from config.constants import SUCCESS_COLOR, ERROR_COLOR, INFO_COLOR

class Economy(commands.Cog):
    """Экономические команды SapphireBot."""
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="balance",
        description="Показать баланс пользователя"
    )
    async def balance(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        """Показывает баланс пользователя или свой собственный."""
        member = member or inter.author
        balance = EconomyService.get_balance(str(member.id))
        embed = make_embed(
            title=f"Кошелёк {member.display_name}",
            description=f"Ваш баланс: **{balance} 💎**",
            color=INFO_COLOR,
            thumbnail=member.display_avatar.url
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="add_balance",
        description="Добавить баланс пользователю (только staff)"
    )
    @require_staff()
    async def add_balance(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int = commands.Param(ge=1), reason: str = "Причина не указана"):
        """Добавляет баланс пользователю. Только для staff."""
        new_balance = EconomyService.add_balance(str(member.id), amount)
        embed = make_embed(
            title="Баланс пополнен",
            description=f"Пользователь: {member.mention}\nСумма: +{amount} 💎\nНовый баланс: {new_balance} 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=SUCCESS_COLOR
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="remove_balance",
        description="Убрать баланс у пользователя (только staff)"
    )
    @require_staff()
    async def remove_balance(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int = commands.Param(ge=1), reason: str = "Причина не указана"):
        """Уменьшает баланс пользователя. Только для staff."""
        new_balance = EconomyService.remove_balance(str(member.id), amount)
        embed = make_embed(
            title="Баланс уменьшен",
            description=f"Пользователь: {member.mention}\nСумма: -{amount} 💎\nНовый баланс: {new_balance} 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=INFO_COLOR
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="set_balance",
        description="Установить баланс пользователю (только staff)"
    )
    @require_staff()
    async def set_balance(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int = commands.Param(ge=0), reason: str = "Причина не указана"):
        """Устанавливает баланс пользователя. Только для staff."""
        EconomyService.set_balance(str(member.id), amount)
        embed = make_embed(
            title="Баланс установлен",
            description=f"Пользователь: {member.mention}\nНовый баланс: {amount} 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=INFO_COLOR
        )
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))