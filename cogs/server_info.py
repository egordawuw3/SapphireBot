import disnake
from disnake.ext import commands
from datetime import datetime, timezone

class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_time_ago(self, delta_days):
        years = delta_days // 365
        months = (delta_days % 365) // 30
        
        if years == 0:
            if months == 0:
                return "менее месяца назад"
            else:
                return f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'} назад"
        else:
            year_text = f"{years} {'год' if years == 1 else 'года' if 2 <= years <= 4 else 'лет'}"
            if months == 0:
                return f"{year_text} назад"
            else:
                month_text = f"{months} {'месяц' if months == 1 else 'месяца' if 2 <= months <= 4 else 'месяцев'}"
                return f"{year_text} и {month_text} назад"

    @commands.slash_command(
        name="serverinfo",
        description="Показывает информацию о сервере"
    )
    async def server_info(self, inter: disnake.ApplicationCommandInteraction):
        guild = inter.guild
        
        # Подсчет участников по статусам
        total_members = len(guild.members)
        humans = len([m for m in guild.members if not m.bot])
        bots = len([m for m in guild.members if m.bot])
        
        online = len([m for m in guild.members if str(m.status) == "online"])
        idle = len([m for m in guild.members if str(m.status) == "idle"])
        dnd = len([m for m in guild.members if str(m.status) == "dnd"])
        offline = len([m for m in guild.members if str(m.status) == "offline"])

        # Подсчет каналов
        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        forum_channels = len([c for c in guild.channels if isinstance(c, disnake.ForumChannel)])
        announcement_channels = len([c for c in guild.channels if isinstance(c, disnake.TextChannel) and c.is_news()])

        # Создаем встроенное сообщение
        embed = disnake.Embed(
            title=f"Информация о сервере {guild.name} • 💎",
            color=disnake.Color.blue()
        )

        # Участники
        embed.add_field(
            name="Участники:",
            value=(
                f"👥 Всего: {total_members}\n"
                f"👤 Людей: {humans}\n"
                f"🤖 Ботов: {bots}"
            ),
            inline=True
        )

        # По статусам
        embed.add_field(
            name="По статусам:",
            value=(
                f"🟢 В сети: {online}\n"
                f"🌙 Неактивен: {idle}\n"
                f"⛔ Не беспокоить: {dnd}\n"
                f"⚪ Не в сети: {offline}"
            ),
            inline=True
        )

        # Каналы
        embed.add_field(
            name="Каналы:",
            value=(
                f"💬 Всего: {total_channels}\n"
                f"# Текстовых: {text_channels}\n"
                f"💭 Форумов: {forum_channels}\n"
                f"🔊 Голосовых: {voice_channels}\n"
                f"📢 Объявления: {announcement_channels}"
            ),
            inline=True
        )

        # Владелец и дата создания
        created_days = (datetime.now(timezone.utc) - guild.created_at).days
        
        embed.add_field(
            name="Владелец:",
            value=f"{guild.owner.name}",
            inline=True
        )

        embed.add_field(
            name="Уровень проверки:",
            value=f"{str(guild.verification_level).capitalize()}",
            inline=True
        )

        embed.add_field(
            name="Дата создания:",
            value=(
                f"{guild.created_at.strftime('%d %B %Y г.')}\n"
                f"{self.format_time_ago(created_days)}"
            ),
            inline=True
        )

        # ID сервера
        embed.set_footer(text=f"ID: {guild.id}")

        # Устанавливаем иконку сервера
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(ServerInfo(bot))