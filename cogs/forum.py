import disnake
from disnake.ext import commands
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR

logger = logging.getLogger(__name__)

class Forum(commands.Cog):
    """Cog для автоматического сообщения о форуме сервера."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1117014421097697281

    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            logger.error("❌ Канал форума не найден!")
            return
        await channel.purge()
        banner_embed = make_embed(
            title=" ",
            color=INFO_COLOR
        )
        banner_embed.set_image(url="https://media.discordapp.net/attachments/998670555152666645/1364551085074681968/7571b87c738a051c.png?ex=681e83fa&is=681d327a&hm=f0d0a7d9674c302d085277818959a98f06a4f2f8a625ea110aadea39c66d1dd7&=&format=webp&quality=lossless&width=2340&height=1316")
        await channel.send(embed=banner_embed)
        main_embed = make_embed(
            title="Форум",
            description=(
                "<:Sapphire_icon:1159784623266615357> У нас на Сервере ты можешь создавать публикации в "
                "форуме или начать следить за публикациями других людей.\n"
                "\n"
                "<:Sapphire_icon:1159784599010938922> Тематика в ваших публикациях должна соответствовать "
                "[Правилам сервера](https://discord.com/channels/832291503581167636/1362850230181171432) "
                "и сообщества в целом.\n"
                "\n"
                "<:Sapphire_icon:1159785716176388177> Публикация должна иметь в наличии следующие компоненты:\n"
                "- заговолок, намекающий на содержание публикации;\n"
                "- конструктивный и информационный контекст;\n"
                "- тег, соответствующий тематике публикации;"
            ),
            color=INFO_COLOR
        )
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif")
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        await channel.send(embed=main_embed)
        logger.info("✅ Сообщения форума успешно отправлены!")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Forum(bot))