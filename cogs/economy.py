import disnake
from disnake.ext import commands
from utils.database import Database

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()

    def format_number(self, number: int) -> str:
        return "{:,}".format(number).replace(",", " ")

    @commands.slash_command(
        name="balance",
        description="Показать баланс пользователя"
    )
    async def balance(self, inter: disnake.ApplicationCommandInteraction, member: disnake.Member = None):
        member = member or inter.author
        balance = self.db.get_user_balance(str(member.id))

        embed = disnake.Embed(
            title=f"💰 Кошелёк {member.display_name}",
            color=0x2B65EC
        )
        
        embed.add_field(
            name="Баланс",
            value=f"```{self.format_number(balance)} 💎```",
            inline=False
        )
        
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        
        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Economy(bot))