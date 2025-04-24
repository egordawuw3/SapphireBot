import disnake
from disnake.ext import commands
import asyncio
from datetime import datetime

class Staff(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.staff_role_id = 1207281299849744385

    async def check_staff(self, inter: disnake.ApplicationCommandInteraction) -> bool:
        """Проверка на наличие роли staff"""
        staff_role = inter.guild.get_role(self.staff_role_id)
        if staff_role not in inter.author.roles:
            embed = disnake.Embed(
                title="❌ Ошибка доступа",
                description="У вас недостаточно прав для использования этой команды!",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @commands.slash_command(
        name="ban",
        description="Забанить пользователя с указанием причины"
    )
    async def ban(
        self, 
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        reason: str = "Причина не указана",
        delete_messages_days: int = commands.Param(
            default=0,
            description="Удалить сообщения пользователя за последние N дней (0-7)",
            ge=0,
            le=7
        )
    ):
        if not await self.check_staff(inter):
            return
        
        if member.top_role >= inter.author.top_role:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description="Вы не можете забанить участника с равной или более высокой ролью!",
                color=0xff0000
            )
            return await inter.response.send_message(embed=embed, ephemeral=True)

        try:
            await member.ban(reason=reason, delete_message_days=delete_messages_days)
            
            embed = disnake.Embed(
                title="🔨 Бан пользователя",
                color=0xff0000,
                timestamp=datetime.now()
            )
            embed.add_field(name="Забанен пользователь", value=f"{member.mention} (`{member.id}`)", inline=False)
            embed.add_field(name="Модератор", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Причина", value=reason, inline=True)
            if delete_messages_days > 0:
                embed.add_field(name="Удалены сообщения за", value=f"{delete_messages_days} дней", inline=True)
            
            await inter.response.send_message(embed=embed)
            
            try:
                dm_embed = disnake.Embed(
                    title="🔨 Вы были забанены",
                    description=f"**Сервер:** {inter.guild.name}\n**Причина:** {reason}",
                    color=0xff0000
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось забанить пользователя: {str(e)}",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="unban",
        description="Разбанить пользователя по ID"
    )
    async def unban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        user_id: str = commands.Param(description="ID пользователя для разбана")
    ):
        if not await self.check_staff(inter):
            return
        
        try:
            user = await self.bot.fetch_user(int(user_id))
            await inter.guild.unban(user)
            
            embed = disnake.Embed(
                title="🔓 Разбан пользователя",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Разбанен пользователь", value=f"{user.mention} (`{user.id}`)", inline=False)
            embed.add_field(name="Модератор", value=f"{inter.author.mention}", inline=True)
            
            await inter.response.send_message(embed=embed)
            
        except ValueError:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description="Указан неверный ID пользователя!",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось разбанить пользователя: {str(e)}",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="mute",
        description="Замутить пользователя на определенное время"
    )
    async def mute(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member,
        duration: int = commands.Param(description="Длительность мута в минутах"),
        reason: str = "Причина не указана"
    ):
        if not await self.check_staff(inter):
            return
        
        if member.top_role >= inter.author.top_role:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description="Вы не можете замутить участника с равной или более высокой ролью!",
                color=0xff0000
            )
            return await inter.response.send_message(embed=embed, ephemeral=True)

        try:
            await member.timeout(duration=duration * 60, reason=reason)
            
            embed = disnake.Embed(
                title="🔇 Мут пользователя",
                color=0xff9900,
                timestamp=datetime.now()
            )
            embed.add_field(name="Замучен пользователь", value=f"{member.mention} (`{member.id}`)", inline=False)
            embed.add_field(name="Модератор", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Длительность", value=f"{duration} минут", inline=True)
            embed.add_field(name="Причина", value=reason, inline=True)
            
            await inter.response.send_message(embed=embed)
            
            try:
                dm_embed = disnake.Embed(
                    title="🔇 Вы были замучены",
                    description=f"**Сервер:** {inter.guild.name}\n**Длительность:** {duration} минут\n**Причина:** {reason}",
                    color=0xff9900
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось замутить пользователя: {str(e)}",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="unmute",
        description="Размутить пользователя"
    )
    async def unmute(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member
    ):
        if not await self.check_staff(inter):
            return

        try:
            await member.timeout(duration=0)
            
            embed = disnake.Embed(
                title="🔊 Размут пользователя",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Размучен пользователь", value=f"{member.mention} (`{member.id}`)", inline=False)
            embed.add_field(name="Модератор", value=f"{inter.author.mention}", inline=True)
            
            await inter.response.send_message(embed=embed)
            
            try:
                dm_embed = disnake.Embed(
                    title="🔊 Вы были размучены",
                    description=f"**Сервер:** {inter.guild.name}",
                    color=0x00ff00
                )
                await member.send(embed=dm_embed)
            except:
                pass
                
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось размутить пользователя: {str(e)}",
                color=0xff0000
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="clear",
        description="Очистить сообщения в канале"
    )
    async def clear(
        self,
        inter: disnake.ApplicationCommandInteraction,
        amount: int = commands.Param(description="Количество сообщений для удаления", ge=1, le=1000)
    ):
        if not await self.check_staff(inter):
            return
        
        try:
            await inter.response.defer(ephemeral=True)
            deleted = await inter.channel.purge(limit=amount)
            
            embed = disnake.Embed(
                title="🧹 Очистка чата",
                description=f"Удалено {len(deleted)} сообщений",
                color=0x00ff00,
                timestamp=datetime.now()
            )
            embed.add_field(name="Модератор", value=f"{inter.author.mention}", inline=True)
            embed.add_field(name="Канал", value=f"{inter.channel.mention}", inline=True)
            
            msg = await inter.channel.send(embed=embed)
            await asyncio.sleep(5)
            await msg.delete()
            
            await inter.edit_original_message(
                embed=disnake.Embed(
                    description=f"✅ Успешно удалено {len(deleted)} сообщений",
                    color=0x00ff00
                )
            )
            
        except Exception as e:
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось очистить сообщения: {str(e)}",
                color=0xff0000
            )
            await inter.edit_original_message(embed=embed)

def setup(bot):
    bot.add_cog(Staff(bot))