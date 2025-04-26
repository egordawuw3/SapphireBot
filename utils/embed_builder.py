import disnake
from typing import Optional, List, Dict, Any, Union

class EmbedBuilder:
    """Класс для создания красивых эмбедов"""
    
    @staticmethod
    def success(title: str, description: str, **kwargs) -> disnake.Embed:
        """Создает эмбед успешного действия"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=0x2ecc71,  # Зеленый
            **kwargs
        )
        return embed
    
    @staticmethod
    def error(title: str, description: str, **kwargs) -> disnake.Embed:
        """Создает эмбед ошибки"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=0xe74c3c,  # Красный
            **kwargs
        )
        return embed
    
    @staticmethod
    def info(title: str, description: str, **kwargs) -> disnake.Embed:
        """Создает информационный эмбед"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=0x3498db,  # Синий
            **kwargs
        )
        return embed
    
    @staticmethod
    def warning(title: str, description: str, **kwargs) -> disnake.Embed:
        """Создает предупреждающий эмбед"""
        embed = disnake.Embed(
            title=title,
            description=description,
            color=0xf39c12,  # Оранжевый
            **kwargs
        )
        return embed
    
    @staticmethod
    def level_up(user: disnake.Member, level: int, color: int, emoji: str) -> disnake.Embed:
        """Создает эмбед повышения уровня"""
        embed = disnake.Embed(
            title=f"{emoji} Новый уровень!",
            description=f"🎉 Поздравляем, {user.mention}!\nВы достигли **{level}** уровня!",
            color=color
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        return embed
    
    @staticmethod
    def rank(user: disnake.Member, level: int, xp: int, next_level_xp: Union[int, float], 
             color: int, emoji: str) -> disnake.Embed:
        """Создает эмбед ранга пользователя"""
        embed = disnake.Embed(
            title=f"{emoji} Статистика {user.display_name}",
            color=color
        )
        
        if next_level_xp != float('inf'):
            progress = f"{xp}/{next_level_xp}"
            remaining = f"До следующего уровня: {next_level_xp - xp} XP"
        else:
            progress = f"{xp}"
            remaining = "Максимальный уровень достигнут! 🎊"
            
        embed.add_field(name="Уровень", value=str(level), inline=True)
        embed.add_field(name="Опыт", value=progress, inline=True)
        embed.add_field(name="Прогресс", value=remaining, inline=False)
        embed.set_thumbnail(url=user.display_avatar.url)
        
        return embed
    
    @staticmethod
    def leaderboard(users_data: List[Dict[str, Any]], user_objects: Dict[str, disnake.User]) -> disnake.Embed:
        """Создает эмбед таблицы лидеров"""
        embed = disnake.Embed(
            title="🏆 Таблица лидеров",
            color=0xFFD700  # Золотой
        )
        
        for index, data in enumerate(users_data, 1):
            user_id = data["user_id"]
            user = user_objects.get(user_id)
            
            if user:
                medal = "👑" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "✨"
                embed.add_field(
                    name=f"{medal} #{index} {user.name}",
                    value=f"Уровень: {data['level']} | XP: {data['xp']}",
                    inline=False
                )
        
        return embed
    
    @staticmethod
    def now_playing(title: str, url: str, thumbnail: str, requester: disnake.Member, 
                    duration: str) -> disnake.Embed:
        """Создает эмбед текущего воспроизведения"""
        embed = disnake.Embed(
            title="🎵 Сейчас играет",
            description=f"**{title}**",
            color=0x3498db  # Синий
        )
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name="Запросил", value=requester.mention, inline=True)
        embed.add_field(name="Длительность", value=duration, inline=True)
        embed.add_field(name="Ссылка", value=f"[YouTube]({url})", inline=False)
        
        return embed