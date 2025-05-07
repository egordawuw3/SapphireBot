import disnake
from disnake.ext import commands

class Recruitment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = 1362485356594724874
        
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            print("❌ Канал набора не найден!")
            return
            
        # Очищаем канал от предыдущих сообщений
        await channel.purge()
            
        # Отправляем баннер через embed
        banner_embed = disnake.Embed(color=0x2B65EC)  # Изменен цвет на синий
        banner_embed.set_image(url="https://media.discordapp.net/attachments/998671608652759081/1369736870380179587/photo_2025-05-07_20-57-00.jpg?ex=681cf25e&is=681ba0de&hm=f998ab2a81655fdd6876f546ed6628232fc4790d2125a271643b26e4242bf9d2&=&format=webp&width=1100&height=618")
        await channel.send(embed=banner_embed)
        
        # Создаем основной embed с текстом
        main_embed = disnake.Embed(color=0x2B65EC)
        main_embed.description = (
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
        )
        
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif?ex=6807d169&is=68067fe9&hm=f5c56aa0b94df799be1732a2918cc5ffc3eece88c1f567a323362f840830b102&")
        
        # Обновляем подпись с иконкой
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")
        
        await channel.send(embed=main_embed)
        
        print("✅ Сообщения о наборе успешно отправлены!")

def setup(bot):
    bot.add_cog(Recruitment(bot))