import disnake
from disnake.ext import commands
import yt_dlp
import asyncio
import logging
import re
from utils.embed_builder import EmbedBuilder
from config.constants import MAX_SONG_DURATION

logger = logging.getLogger("sapphire_bot.music")

# Настройки для yt-dlp
ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ydl = yt_dlp.YoutubeDL(ydl_opts)
        self.active_players = {}  # Словарь для отслеживания активных плееров

    def is_valid_youtube_url(self, url):
        """Проверяет, является ли URL действительной ссылкой на YouTube"""
        youtube_regex = (
            r'(https?://)?(www\.)?'
            r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
        )
        match = re.match(youtube_regex, url)
        return bool(match)

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
        if not self.is_valid_youtube_url(url):
            return await inter.response.send_message("❌ Пожалуйста, используйте только корректные ссылки с YouTube!", ephemeral=True)

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
            try:
                data = await loop.run_in_executor(None, lambda: self.ydl.extract_info(url, download=False))
            except Exception as e:
                logger.error(f"Ошибка при получении информации о видео: {e}")
                return await inter.followup.send(f"❌ Не удалось получить информацию о видео: {str(e)}", ephemeral=True)
            
            if "entries" in data:
                data = data["entries"][0]

            # Проверяем длительность видео (ограничиваем до 10 минут)
            if data.get('duration', 0) > 600:  # 10 минут в секундах
                return await inter.followup.send("❌ Видео слишком длинное. Максимальная длительность - 10 минут.", ephemeral=True)

            # Воспроизводим аудио
            try:
                vc.play(disnake.FFmpegPCMAudio(data['url']))
                
                # Сохраняем информацию о текущем плеере
                self.active_players[inter.guild.id] = {
                    'title': data['title'],
                    'url': url,
                    'requester': inter.author.id,
                    'channel': inter.channel.id
                }
                
                embed = disnake.Embed(
                    title="🎵 Сейчас играет",
                    description=f"**{data['title']}**",
                    color=0x3498db
                )
                embed.set_thumbnail(url=data.get('thumbnail', ''))
                embed.add_field(name="Запросил", value=inter.author.mention, inline=True)
                embed.add_field(name="Длительность", value=self.format_duration(data.get('duration', 0)), inline=True)
                
                await inter.followup.send(embed=embed)
                logger.info(f"Пользователь {inter.author.id} включил музыку: {data['title']}")
                
            except Exception as e:
                logger.error(f"Ошибка при воспроизведении аудио: {e}")
                await inter.followup.send(f"❌ Ошибка при воспроизведении: {str(e)}", ephemeral=True)

        except Exception as e:
            logger.error(f"Общая ошибка в команде mus: {e}")
            await inter.followup.send(f"❌ Ошибка при воспроизведении: {str(e)}", ephemeral=True)

    @commands.slash_command(name="stop", description="Остановить воспроизведение")
    async def stop(self, inter: disnake.ApplicationCommandInteraction):
        """Остановить воспроизведение"""
        if not inter.guild.voice_client:
            return await inter.response.send_message("❌ Бот не в голосовом канале!", ephemeral=True)
        
        # Проверяем, находится ли пользователь в том же голосовом канале
        if not inter.author.voice or inter.author.voice.channel != inter.guild.voice_client.channel:
            return await inter.response.send_message("❌ Вы должны быть в том же голосовом канале, что и бот!", ephemeral=True)
        
        inter.guild.voice_client.stop()
        
        # Удаляем информацию о плеере
        if inter.guild.id in self.active_players:
            del self.active_players[inter.guild.id]
            
        await inter.response.send_message("⏹️ Воспроизведение остановлено!")
        logger.info(f"Пользователь {inter.author.id} остановил воспроизведение музыки")

    def format_duration(self, seconds):
        """Форматирует длительность в секундах в формат MM:SS"""
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes}:{seconds:02d}"

def setup(bot):
    bot.add_cog(Music(bot))