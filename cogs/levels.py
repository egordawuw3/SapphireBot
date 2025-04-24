import json
import math
import disnake
from disnake.ext import commands

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.users_data = {}
        self.xp_per_message = 15
        self.base_xp = 100
        self.max_level = 50
        self.load_data()

    def load_data(self):
        """Загружает данные пользователей из JSON файла"""
        try:
            with open('levels_data.json', 'r') as f:
                self.users_data = json.load(f)
        except FileNotFoundError:
            self.users_data = {}
            self.save_data()

    def save_data(self):
        """Сохраняет данные пользователей в JSON файл"""
        with open('levels_data.json', 'w') as f:
            json.dump(self.users_data, f, indent=4)

    async def update_roles(self, member, level):
        """Обновляет роли пользователя в зависимости от уровня"""
        role_levels = {
            1: 1364889084098510868,
            5: 1364889174280372274,
            10: 1364889171222855760,
            15: 1364889168592769104,
            25: 1364889165333925968,
            35: 1364889161886204054,
            45: 1364889851949879339,
            50: 1364889574639407116
        }
        
        try:
            # Получаем все роли, которые должны быть у пользователя
            roles_to_add = []
            for req_level, role_id in role_levels.items():
                if level >= req_level:
                    role = member.guild.get_role(role_id)
                    if role and role not in member.roles:
                        roles_to_add.append(role)
            
            # Применяем изменения
            if roles_to_add:
                await member.add_roles(*roles_to_add)
                
                # Отправляем сообщение о новых ролях в канал spam
                spam_channel = None
                for channel in member.guild.channels:
                    if channel.name.lower() == 'spam':
                        spam_channel = channel
                        break
                
                if spam_channel:
                    role_names = [role.name for role in roles_to_add]
                    embed = disnake.Embed(
                        title="🎭 Новые роли!",
                        description=f"🎉 {member.mention} получает новые роли за достижение {level} уровня:\n" + 
                                  "\n".join([f"• {role}" for role in role_names]),
                        color=self.get_level_color(level)
                    )
                    await spam_channel.send(embed=embed)
                    
        except Exception as e:
            print(f"Ошибка при обновлении ролей: {e}")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
            
        # Проверяем, не является ли канал спам-каналом
        if message.channel.name.lower().find('spam') != -1:
            return
            
        user_id = str(message.author.id)
        if user_id not in self.users_data:
            self.users_data[user_id] = {"xp": 0, "level": 0}
            
        old_level = self.users_data[user_id]["level"]
        self.users_data[user_id]["xp"] += self.xp_per_message
        new_level = self.calculate_level(self.users_data[user_id]["xp"])
        self.users_data[user_id]["level"] = new_level
        
        if new_level > old_level:
            # Ищем канал spam
            spam_channel = None
            for channel in message.guild.channels:
                if channel.name.lower() == 'spam':
                    spam_channel = channel
                    break
            
            if spam_channel:
                embed = disnake.Embed(
                    title=f"{self.get_level_emoji(new_level)} Новый уровень!",
                    description=f"🎉 Поздравляем, {message.author.mention}!\nВы достигли **{new_level}** уровня!",
                    color=self.get_level_color(new_level)
                )
                embed.set_thumbnail(url=message.author.display_avatar.url)
                await spam_channel.send(embed=embed)
                
            # Обновляем роли пользователя
            await self.update_roles(message.author, new_level)
            
        self.save_data()

    @commands.slash_command(
        name="rank",
        description="Показать ваш текущий уровень и опыт"
    )
    async def rank(self, inter: disnake.ApplicationCommandInteraction):
        user_id = str(inter.author.id)
        if user_id not in self.users_data:
            await inter.response.send_message(
                "У вас пока нет уровня. Начните общаться!",
                ephemeral=True
            )
            return
            
        user_data = self.users_data[user_id]
        current_xp = user_data["xp"]
        current_level = user_data["level"]
        xp_for_next = self.calculate_xp_for_next_level(current_level)
        
        embed = disnake.Embed(
            title=f"{self.get_level_emoji(current_level)} Статистика {inter.author.display_name}",
            color=self.get_level_color(current_level)
        )
        
        if current_level < self.max_level:
            progress = f"{current_xp}/{xp_for_next}"
            remaining = f"До следующего уровня: {xp_for_next - current_xp} XP"
        else:
            progress = f"{current_xp}"
            remaining = "Максимальный уровень достигнут! 🎊"
            
        embed.add_field(name="Уровень", value=str(current_level), inline=True)
        embed.add_field(name="Опыт", value=progress, inline=True)
        embed.add_field(name="Прогресс", value=remaining, inline=False)
        embed.set_thumbnail(url=inter.author.display_avatar.url)
        
        await inter.response.send_message(embed=embed)

    @commands.slash_command(
        name="leaderboard",
        description="Показать таблицу лидеров"
    )
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        sorted_users = sorted(
            self.users_data.items(),
            key=lambda x: (x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:10]
        
        embed = disnake.Embed(
            title="🏆 Таблица лидеров",
            color=0xFFD700
        )
        
        for index, (user_id, data) in enumerate(sorted_users, 1):
            user = await self.bot.get_or_fetch_user(int(user_id))
            if user:
                medal = "👑" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else "✨"
                embed.add_field(
                    name=f"{medal} #{index} {user.name}",
                    value=f"Уровень: {data['level']} | XP: {data['xp']}",
                    inline=False
                )
        
        await inter.response.send_message(embed=embed)

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
        if level >= 40:
            return "🌟"
        elif level >= 30:
            return "💎"
        elif level >= 20:
            return "🔮"
        elif level >= 10:
            return "⭐"
        else:
            return "✨"
            
    def get_level_color(self, level):
        """Возвращает цвет в зависимости от уровня"""
        if level >= 40:
            return 0xFF0000  # Красный
        elif level >= 30:
            return 0xFFA500  # Оранжевый
        elif level >= 20:
            return 0xFFFF00  # Желтый
        elif level >= 10:
            return 0x00FF00  # Зеленый
        else:
            return 0x0000FF  # Синий

def setup(bot):
    bot.add_cog(Levels(bot))