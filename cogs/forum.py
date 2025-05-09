import disnake
from disnake.ext import commands

class Recruitment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = 1117014421097697281
        
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

class Forum(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.target_channel_id = 1117014421097697281
        
    @commands.Cog.listener()
    async def on_ready(self):
        channel = self.bot.get_channel(self.target_channel_id)
        if not channel:
            print("❌ Канал форума не найден!")
            return
            
        # Очищаем канал от предыдущих сообщений
        await channel.purge()
            
        # Отправляем баннер через embed
        banner_embed = disnake.Embed(color=0x2B65EC)
        banner_embed.set_image(url="https://media.discordapp.net/attachments/998670555152666645/1364551085074681968/7571b87c738a051c.png?ex=681e83fa&is=681d327a&hm=f0d0a7d9674c302d085277818959a98f06a4f2f8a625ea110aadea39c66d1dd7&=&format=webp&quality=lossless&width=2340&height=1316")
        await channel.send(embed=banner_embed)
            
        # Создаем основной embed с текстом
        main_embed = disnake.Embed(color=0x2B65EC)
        main_embed.description = (
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
        )
        
        main_embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif")
        main_embed.set_footer(text="С уважением, администрация Sapphire Creators 💎", icon_url="https://cdn.discordapp.com/emojis/1369745518418198778.png")

        
        await channel.send(embed=main_embed)
        
        print("✅ Сообщения форума успешно отправлены!")

def setup(bot):
    bot.add_cog(Forum(bot))