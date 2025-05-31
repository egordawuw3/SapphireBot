import disnake
from disnake.ext import commands
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR

logger = logging.getLogger(__name__)

class Resource(commands.Cog):
    """Cog для автоматического сообщения о ресурсах сервера."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1364554388349255746
        
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            logger.error("❌ Канал ресурсов не найден!")
            return
            
        # Очищаем канал от предыдущих сообщений
        await channel.purge()
            
        # Отправляем баннер через embed
        banner_embed = make_embed(
            title=" ",
            color=INFO_COLOR
        )
        banner_embed.set_image(url="https://media.discordapp.net/attachments/998670555152666645/1364551085511151617/61be0a61eaef0bf6.png?ex=681e83fa&is=681d327a&hm=665710c039e2181fd7d886e52fc4510f10d90b7c8c814ff05ff4aa3430610690&=&format=webp&quality=lossless&width=2340&height=1316")
        await channel.send(embed=banner_embed)
            
        # Создаем основной embed с текстом
        main_embed = make_embed(
            title="Ресурсы",
            description=(
                "<:Sapphire_icon:1159784599010938922> Данный форум создан, чтобы Вы могли найти нужные вам "
                "шрифты, аудио, эмодзи, пресеты, луты, гиф, эффекты, фото и.т.п.\n"
                "\n"
                "<:Sapphire_icon:1159785716176388177> Также вы сами можете публиковать данные публикации. "
                "Какие нужно соблюдать правила?\n"
                "- заговолок, намекающий на содержание публикации;\n"
                "- конструктивный и информационный контекст;\n"
                "- тег, соответствующий тематике публикации;\n"
                "\n"
                "<:Sapphire_icon:1159787682734542869> Остались вопросы? Вам [сюда](https://discord.com/channels/832291503581167636/1054101394270978119)."
            ),
            color=INFO_COLOR
        )
        
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif")
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        
        await channel.send(embed=main_embed)
        
        logger.info("✅ Сообщения ресурсов успешно отправлены!")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Resource(bot))