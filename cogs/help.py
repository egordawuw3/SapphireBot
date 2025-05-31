import disnake
from disnake.ext import commands
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR

class Help(commands.Cog):
    """Команды помощи по SapphireBot."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="help",
        description="Показать список всех доступных команд"
    )
    async def help(self, inter: disnake.ApplicationCommandInteraction) -> None:
        fields = [
            {
                "name": "🎮 Система уровней",
                "value": """
`/rank` - Показать ваш текущий уровень и опыт
`/leaderboard` - Показать таблицу лидеров
                """,
                "inline": False
            },
            {
                "name": "🤖 ИИ-чат",
                "value": """
`/ai` - Создать приватный чат с ИИ
`/ask` - Задать вопрос ИИ в приватном чате
                """,
                "inline": False
            },
            {
                "name": "🛠️ Утилиты",
                "value": """
`/ping` - Проверить работоспособность бота
`/help` - Показать это сообщение
                """,
                "inline": False
            },
            {
                "name": "💸 Экономика",
                "value": """
`/balance` - Показать ваш баланс или баланс другого пользователя
                """,
                "inline": False
            }
        ]
        embed = make_embed(
            title="Помощь по командам",
            description="Список всех доступных команд бота",
            color=INFO_COLOR,
            fields=fields,
            image="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif"
        )
        await inter.response.send_message(embed=embed)

def setup(bot: commands.Bot) -> None:
    """Добавляет cog Help в бота."""
    bot.add_cog(Help(bot))