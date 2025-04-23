import disnake
from disnake.ext import commands
import yt_dlp
import asyncio

# Настройки yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioformat': 'mp3',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)

    @commands.slash_command(
        name="mus",
        description="Включить музыку с YouTube"
    )
    async def mus(
        self,
        inter: disnake.ApplicationCommandInteraction,
        url: str = commands.Param(description="Ссылка на YouTube видео")
    ):
        # Проверяем, что это ссылка YouTube
        if "youtube.com" not in url and "youtu.be" not in url:
            return await inter.response.send_message("❌ Пожалуйста, используйте только ссылки с YouTube!", ephemeral=True)

        if not inter.author.voice:
            return await inter.response.send_message("❌ Вы должны быть в голосовом канале!", ephemeral=True)

        await inter.response.defer()

        try:
            if not inter.guild.voice_client:
                vc = await inter.author.voice.channel.connect()
            else:
                vc = inter.guild.voice_client
                if vc.is_playing():
                    vc.stop()

            # Получаем информацию о видео
            loop = self.bot.loop
            data = await loop.run_in_executor(None, lambda: self.ydl.extract_info(url, download=False))
            
            if "entries" in data:
                data = data["entries"][0]

            # Воспроизводим аудио
            vc.play(disnake.FFmpegPCMAudio(data['url']))
            
            await inter.followup.send(f"🎵 Сейчас играет: **{data['title']}**")

        except Exception as e:
            await inter.followup.send(f"❌ Ошибка при воспроизведении: {str(e)}", ephemeral=True)

    @commands.slash_command(name="stop")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        """Остановить воспроизведение"""
        if not inter.guild.voice_client:
            return await inter.response.send_message("❌ Бот не в голосовом канале!", ephemeral=True)
        
        inter.guild.voice_client.stop()
        await inter.response.send_message("⏹️ Воспроизведение остановлено!")

def setup(bot):
    bot.add_cog(Music(bot))