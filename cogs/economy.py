import disnake
from disnake.ext import commands
from utils.embed_utils import make_embed
from utils.economy_service import EconomyService
from utils.permissions import require_staff
from config.constants import SUCCESS_COLOR, ERROR_COLOR, INFO_COLOR, EMOJI_GOLD, EMOJI_SILVER, EMOJI_BRONZE, EMBED_COLOR, WARNING_COLOR

class Economy(commands.Cog):
    """Экономические команды SapphireBot."""
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="bal",
        description="Показать баланс пользователя"
    )
    async def bal(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
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
        name="add",
        description="Выдать монеты юзеру (мод, раз в 24ч)"
    )
    @require_staff()
    async def add(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int = commands.Param(ge=1), reason: str = "Причина не указана"):
        """Выдать монеты пользователю (только staff)."""
        new_balance = EconomyService.add_balance(str(member.id), amount)
        embed = make_embed(
            title="Баланс пополнен",
            description=f"Пользователь: {member.mention}\nСумма: +{amount} 💎\nНовый баланс: {new_balance} 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=SUCCESS_COLOR
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="remove",
        description="Забрать монеты у юзера (мод)"
    )
    @require_staff()
    async def remove(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, amount: int = commands.Param(ge=1), reason: str = "Причина не указана"):
        """Забрать монеты у пользователя (только staff)."""
        new_balance = EconomyService.remove_balance(str(member.id), amount)
        embed = make_embed(
            title="Баланс уменьшен",
            description=f"Пользователь: {member.mention}\nСумма: -{amount} 💎\nНовый баланс: {new_balance} 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=INFO_COLOR
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="reset",
        description="Аннулировать баланс юзера (мод)"
    )
    @require_staff()
    async def reset(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member, reason: str = "Причина не указана"):
        """Аннулирует баланс пользователя (только staff)."""
        EconomyService.reset_balance(str(member.id))
        embed = make_embed(
            title="Баланс аннулирован",
            description=f"Пользователь: {member.mention}\nБаланс сброшен до 0 💎\nМодератор: {inter.author.mention}\nПричина: {reason}",
            color=WARNING_COLOR
        )
        await inter.response.send_message(embed=embed)

    @commands.slash_command(name="scoreboard", description="Таблица лидеров по монетам")
    async def scoreboard(self, inter: disnake.ApplicationCommandInteraction):
        """Показывает топ-10 пользователей по балансу."""
        from utils.economy_service import get_top_balances
        top = await get_top_balances(10)
        if not top:
            await inter.send(embed=make_embed(
                title="Таблица лидеров пуста",
                description="Пока никто не заработал монет.",
                color=ERROR_COLOR
            ), ephemeral=True)
            return
        medals = [EMOJI_GOLD, EMOJI_SILVER, EMOJI_BRONZE]
        lines = []
        for i, (user_id, balance) in enumerate(top, 1):
            medal = medals[i-1] if i <= 3 else f"`{i}`"
            try:
                user = await self.bot.fetch_user(int(user_id))
                user_mention = user.mention
            except Exception:
                user_mention = f"<@{user_id}>"
            lines.append(f"{medal} {user_mention} — **{balance} монет**")
        embed = make_embed(
            title="🏆 Таблица лидеров по монетам",
            description="\n".join(lines),
            color=EMBED_COLOR
        )
        embed.set_footer(text="Топ-10 по балансу")
        await inter.send(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))