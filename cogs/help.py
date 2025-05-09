import disnake
from disnake.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name="help",
        description="Показать список всех доступных команд"
    )
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="📚 Помощь по командам",
            description="Список всех доступных команд бота",
            color=0x3498db
        )

        # Секция уровней
        embed.add_field(
            name="🎮 Система уровней",
            value="""
`/rank` - Показать ваш текущий уровень и опыт
`/leaderboard` - Показать таблицу лидеров
            """,
            inline=False
        )


        # Секция AI-чата
        embed.add_field(
            name="🤖 ИИ-чат",
            value="""
`/ai` - Создать приватный чат с ИИ
`/ask` - Задать вопрос ИИ в приватном чате
            """,
            inline=False
        )

        # Секция утилит
        embed.add_field(
            name="🛠️ Утилиты",
            value="""
`/ping` - Проверить работоспособность бота
`/help` - Показать это сообщение
            """,
            inline=False
        )

        # Добавляем изображение
        embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif?ex=6809cba9&is=68087a29&hm=f558c4ed18566a404275a62081737ba50c9342a73fe5169f812f1512e00c412f&")
        
        # Добавляем подпись внизу
        embed.set_footer(
            text="С уважением, администрация Sapphire Creators💎"
        )

        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))