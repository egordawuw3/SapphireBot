import disnake
from disnake.ext import commands
import math
import logging
from datetime import datetime, timedelta
from utils.database import Database
from utils.embed_builder import EmbedBuilder
from config.constants import ROLE_LEVELS, LEVEL_COLORS, LEVEL_EMOJIS, XP_PER_MESSAGE, BASE_XP, MAX_LEVEL, XP_COOLDOWN

logger = logging.getLogger('sapphire_bot.levels')

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database()
        self.xp_per_message = XP_PER_MESSAGE
        self.base_xp = BASE_XP
        self.max_level = MAX_LEVEL
        self.xp_cooldown = XP_COOLDOWN
        self.user_cooldowns = {}

    async def update_roles(self, member, level):
        """Обновляет роли пользователя в зависимости от уровня"""
        try:
            # Находим максимальный доступный уровень
            max_applicable_level = max(
                (req_level for req_level in ROLE_LEVELS if level >= req_level),
                default=None
            )
            
            if max_applicable_level is None:
                return

            # Получаем целевую роль
            target_role_id = ROLE_LEVELS[max_applicable_level]
            target_role = member.guild.get_role(target_role_id)
            
            if not target_role:
                logger.error(f"Роль для уровня {max_applicable_level} не найдена")
                return

            # Получаем все роли из системы уровней
            level_roles = [
                member.guild.get_role(role_id) 
                for role_id in ROLE_LEVELS.values()
                if member.guild.get_role(role_id)
            ]

            # Удаляем все уровневые роли кроме целевой
            roles_to_remove = [r for r in member.roles if r in level_roles and r != target_role]
            
            # Добавляем целевую роль если отсутствует
            if target_role not in member.roles:
                await member.add_roles(target_role)
                
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
            
            # Получаем текущие роли пользователя
            current_roles = member.roles
            
            # Определяем роли для добавления и удаления
            roles_to_add = [r for r in required_roles if r not in current_roles]
            roles_to_remove = [r for r in current_roles if r.id in ROLE_LEVELS.values() and r not in required_roles]
            
            # Применяем изменения
            if roles_to_add:
                await member.add_roles(*roles_to_add)
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove)
                
            # Отправляем сообщение о новых ролях в канал spam
            spam_channel = None
            for channel in member.guild.channels:
                if channel.name.lower() == 'spam':
                    spam_channel = channel
                    break
            
            if spam_channel and (roles_to_add or roles_to_remove):
                role_changes = []
                if roles_to_add:
                    role_names = [role.name for role in roles_to_add]
                    role_changes.append(f"➕ Добавлены: {', '.join(role_names)}")
                if roles_to_remove:
                    role_names = [role.name for role in roles_to_remove]
                    role_changes.append(f"➖ Удалены: {', '.join(role_names)}")
                
                embed = EmbedBuilder.success(
                    title="🎭 Обновление ролей!",
                    description=f"🎉 {member.mention} получает изменения ролей за достижение {level} уровня:\n" + 
                              "\n".join(role_changes)
                )
                await spam_channel.send(embed=embed)
                    
        except Exception as e:
            logger.error(f"Ошибка при обновлении ролей: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Игнорируем сообщения от ботов
        if message.author.bot:
            return
            
        # Проверяем, не является ли канал спам-каналом
        if message.channel.name.lower().find('spam') != -1:
            return
        
        # Проверяем кулдаун
        user_id = str(message.author.id)
        current_time = datetime.now()
        
        if user_id in self.user_cooldowns:
            time_diff = (current_time - self.user_cooldowns[user_id]).total_seconds()
            if time_diff < self.xp_cooldown:  # 0 секунд - условие никогда не выполнится
                return
        
        # Обновляем время последнего сообщения
        self.user_cooldowns[user_id] = current_time
            
        # Получаем данные пользователя
        user_data = self.db.get_user_data(user_id)
            
        old_level = user_data["level"]
        user_data["xp"] += self.xp_per_message
        new_level = self.calculate_level(user_data["xp"])
        user_data["level"] = new_level
        
        # Сохраняем обновленные данные
        self.db.update_user_data(user_id, user_data["xp"], user_data["level"])
        
        # Если уровень повысился
        if new_level > old_level:
            # Ищем канал spam
            spam_channel = None
            for channel in message.guild.channels:
                if channel.name.lower() == 'spam':
                    spam_channel = channel
                    break
            
            if spam_channel:
                embed = EmbedBuilder.level_up(
                    user=message.author,
                    level=new_level,
                    emoji=self.get_level_emoji(new_level)
                )
                await spam_channel.send(embed=embed)
                
            # Обновляем роли пользователя
            await self.update_roles(message.author, new_level)

    @commands.slash_command(
        name="rank",
        description="Показать уровень и опыт участника"
    )
    async def rank(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = commands.Param(
            default=None,
            description="Участник для проверки (оставьте пустым для своего ранга)"
        )
    ):
        target = member or inter.author
        user_id = str(target.id)
        user_data = self.db.get_user_data(user_id)
        
        current_xp = user_data["xp"]
        current_level = user_data["level"]
        xp_for_next = self.calculate_xp_for_next_level(current_level)
        
        embed = EmbedBuilder.rank(
            user=target,
            level=current_level,
            xp=current_xp,
            next_level_xp=xp_for_next,
            color=self.get_level_color(current_level),  # Восстанавливаем параметр цвета
            emoji=self.get_level_emoji(current_level)
        )
        
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="leaderboard",
        description="Показать таблицу лидеров"
    )
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer()
        
        # Получаем топ пользователей
        top_users = self.db.get_top_users(10)
        
        # Получаем объекты пользователей
        user_objects = {}
        for user_data in top_users:
            try:
                user_id = int(user_data["user_id"])
                user = await self.bot.get_or_fetch_user(user_id)
                if user:
                    user_objects[user_data["user_id"]] = user
            except Exception as e:
                logger.error(f"Ошибка при получении пользователя {user_data['user_id']}: {e}")
        
        # Создаем эмбед
        embed = EmbedBuilder.leaderboard(top_users, user_objects)
        
        await inter.followup.send(embed=embed)

    @commands.slash_command(
        name="set_level",
        description="Управление уровнем и опытом пользователя"
    )
    @commands.has_role(1207281299849744385)
    async def set_level(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        action: str = commands.Param(choices=["set", "add", "subtract"]),
        level: int = commands.Param(default=None, ge=0, le=MAX_LEVEL),
        xp: int = commands.Param(default=None, ge=0)
    ):
        """Команда для гибкого управления уровнем и опытом"""
        await inter.response.defer(ephemeral=True)
        try:
            if not (level or xp):
                raise commands.BadArgument("Нужно указать level или xp")

            user_data = self.db.get_user_data(str(member.id))
            current_level = user_data["level"]
            current_xp = user_data["xp"]

            # Обрабатываем уровень
            if level is not None:
                if action == "set":
                    new_level = level
                elif action == "add":
                    new_level = current_level + level
                else: # subtract
                    new_level = max(0, current_level - level)
                
                new_level = min(new_level, MAX_LEVEL)

            # Обрабатываем опыт
            if xp is not None:
                if action == "set":
                    new_xp = xp
                elif action == "add":
                    new_xp = current_xp + xp
                else: # subtract
                    new_xp = max(0, current_xp - xp)
                
                # Всегда пересчитываем уровень по XP
                new_level = self.calculate_level(new_xp)
            else:
                new_xp = current_xp

            # Обновляем данные
            self.db.update_user_data(str(member.id), new_xp, new_level)
            
            # Обновляем роли
            await self.update_roles(member, new_level)
            
            # Формируем сообщение
            changes = []
            if level is not None:
                changes.append(f"• Уровень: {current_level} → {new_level}")
            if xp is not None:
                changes.append(f"• Опыт: {current_xp} → {new_xp}")
            
            embed = EmbedBuilder.success(
                title="✅ Данные обновлены",
                description=f"Пользователь {member.mention}:\n" + "\n".join(changes)
            )
            await inter.edit_original_response(embed=embed)
            
        except Exception as e:
            embed = EmbedBuilder.error(
                title="❌ Ошибка",
                description=f"Ошибка: {str(e)}"
            )
            await inter.followup.send(embed=embed, ephemeral=True)

    def calculate_level(self, xp):
        """Вычисляет уровень на основе количества XP"""
        if xp < self.base_xp:
            return 0
        return min(int(math.log(xp / self.base_xp, 1.5) + 1), self.max_level)

    def calculate_xp_for_next_level(self, current_level):
        """Вычисляет количество XP, необходимое для следующего уровня"""
        if current_level >= self.max_level:
            return float('inf')
        return int(self.base_xp * (1.5 ** (current_level)))

    def get_level_emoji(self, level):
        """Возвращает эмодзи в зависимости от уровня"""
        for min_level, emoji in sorted(LEVEL_EMOJIS.items(), reverse=True):
            if level >= min_level:
                return emoji
        return "✨"
            
    def get_level_color(self, level):
        """Возвращает цвет в зависимости от уровня"""
        for min_level, color in sorted(LEVEL_COLORS.items(), reverse=True):
            if level >= min_level:
                return color
        return 0x0000FF

def setup(bot):
    bot.add_cog(Levels(bot))