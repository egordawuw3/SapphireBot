import disnake
from disnake.ext import commands
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR

logger = logging.getLogger(__name__)

class Recruitment(commands.Cog):
    """Cog для автоматического сообщения о наборе в команду."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.target_channel_id = 1362485356594724874
        
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            logger.error("❌ Канал набора не найден!")
            return
            
        # Очищаем канал от предыдущих сообщений
        await channel.purge()
            
        # Отправляем баннер через embed
        banner_embed = make_embed(
            title=" ",
            color=INFO_COLOR
        )
        banner_embed.set_image(url="https://media.discordapp.net/attachments/998671608652759081/1369736870380179587/photo_2025-05-07_20-57-00.jpg?ex=681cf25e&is=681ba0de&hm=f998ab2a81655fdd6876f546ed6628232fc4790d2125a271643b26e4242bf9d2&=&format=webp&width=1100&height=618")
        await channel.send(embed=banner_embed)
        
        # Создаем основной embed с текстом
        main_embed = make_embed(
            title="Набор в команду",
            description=(
                "<:Sapphire_icon:1159785674929623210> В нашу команду требуются целеустремлённые и увлечённые люди.\n"
                "\n"
                "В команду нужны:\n"
                "- Видео монтажеры\n"
                "(Обработка видео, владение After Effects, Premiere Pro и.т.п.)\n"
                "- Дизайнеры\n"
                "(Создание визаульных проектов; владение Adobe Photoshop и.т.п.)\n"
                "- Дублеры/Дикторы\n"
                "(Озвучка видеоряда, знание других языков приветствуется)\n"
                "- Промоутеры\n"
                "(Техническая часть: искать рекламодателей, клиентов и популизировать проект)\n"
                "- Модераторы\n"
                "(Следят за порядком на сервере и поддерживают активность в голосовых каналах)\n"
                "**Также рассматриваются иные предложения. (Саундизайнеры, сценаристы-ресерчеры, специалисты по нейросетям, программисты и.т.п.)**\n"
                "\n"
                "<:Sapphire_icon:1159787605848756224> Нажмите [сюда](https://docs.google.com/forms/d/e/1FAIpQLSeVd365eIyHLB4qpZRhClNL26xnubMPY9q8-RaFljqBZ1HJZw/viewform?usp=header), чтобы перейти к форме, которую следует заполнить.\n"
            ),
            color=INFO_COLOR
        )
        
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif?")
        
        # Обновляем подпись с иконкой
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        
        await channel.send(embed=main_embed)
        
        logger.info("✅ Сообщения о наборе успешно отправлены!")

def setup(bot: commands.Bot) -> None:
    bot.add_cog(Recruitment(bot))