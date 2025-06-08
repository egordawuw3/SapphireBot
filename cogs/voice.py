import disnake
from disnake.ext import commands
import logging
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR, ERROR_COLOR
from typing import Optional
from datetime import datetime
from utils.database import Database

logger = logging.getLogger(__name__)

class VoiceChannels(commands.Cog):
    """Cog для управления приватными голосовыми каналами."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_channels: dict[int, int] = {}
        self.channel_counter: int = 1
        self.settings_message: Optional[disnake.Message] = None
        self.voice_join_times: dict[int, datetime] = {}
        self.db = Database()

    async def create_settings_message(self, guild: disnake.Guild) -> None:
        """Создает сообщение с настройками в канале Voice Settings."""
        settings_channel = disnake.utils.get(guild.text_channels, name="💽・voice-settings")
        if not settings_channel:
            settings_channel = await guild.create_text_channel("💽・voice-settings")
        else:
            await settings_channel.purge()
        embed = make_embed(
            title="Настройки голосового канала",
            description=(
                "Измените конфигурацию вашей комнаты с помощью панели управления.\n\n"
                "<:Sapphire__icon:1159785635628994601> - Изменить название\n"
                "<:Sapphire_icon:1159785674929623210> - Изменить количество участников\n"
                "<:Sapphire_icon:1159787647712120924> - Выгнать участника"
            ),
            color=INFO_COLOR
        )
        embed.set_image(url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif")
        embed.set_footer(text="С уважением, администрация Sapphire Creators💎")
        components = [
            disnake.ui.Button(style=disnake.ButtonStyle.primary, custom_id="rename", emoji="<:Sapphire__icon:1159785635628994601>", label=""),
            disnake.ui.Button(style=disnake.ButtonStyle.primary, custom_id="limit", emoji="<:Sapphire_icon:1159785674929623210>", label=""),
            disnake.ui.Button(style=disnake.ButtonStyle.danger, custom_id="kick", emoji="<:Sapphire_icon:1159787647712120924>", label="")
        ]
        self.settings_message = await settings_channel.send(embed=embed, components=components)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            await self.create_settings_message(guild)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        try:
            if after.channel and after.channel.name == "「🔑」Create a voice" and after.channel.id not in self.voice_channels:
                existing_channel = next((channel for channel, owner_id in self.voice_channels.items() if owner_id == member.id), None)
                if existing_channel:
                    channel = member.guild.get_channel(existing_channel)
                    if channel:
                        await member.move_to(channel)
                        return
                new_channel = await member.guild.create_voice_channel(
                    name=f"{self.channel_counter}: {member.display_name}",
                    category=after.channel.category,
                    user_limit=5,
                    bitrate=96000
                )
                await new_channel.set_permissions(member, connect=True, manage_channels=True, mute_members=True, deafen_members=True)
                await new_channel.set_permissions(member.guild.default_role, connect=True)
                await member.move_to(new_channel)
                self.voice_channels[new_channel.id] = member.id
                self.channel_counter += 1
            if before.channel and before.channel.id in self.voice_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del self.voice_channels[before.channel.id]
                    await self.update_channel_numbers(before.channel.guild)
            # Отслеживание входа
            if after.channel and (not before.channel or before.channel.id != after.channel.id):
                if member.voice and not member.voice.self_mute and not member.voice.self_deaf:
                    self.voice_join_times[member.id] = datetime.utcnow()
            # Отслеживание выхода
            if before.channel and (not after.channel or before.channel.id != after.channel.id):
                join_time = self.voice_join_times.pop(member.id, None)
                if join_time:
                    duration = datetime.utcnow() - join_time
                    seconds = int(duration.total_seconds())
                    if seconds > 0:
                        self.db.add_user_voice_seconds(str(member.id), seconds)
        except Exception as e:
            logger.error(f"Ошибка в on_voice_state_update: {e}")

    @commands.Cog.listener()
    async def update_channel_numbers(self, guild: disnake.Guild) -> None:
        channels = sorted(
            [(channel_id, channel) for channel_id, owner_id in self.voice_channels.items() if (channel := guild.get_channel(channel_id)) is not None],
            key=lambda x: x[1].position
        )
        for i, (channel_id, channel) in enumerate(channels, 1):
            try:
                current_name = channel.name
                new_name = f"{i}: {current_name.split(':', 1)[1].strip()}"
                await channel.edit(name=new_name)
            except Exception as e:
                logger.error(f"Ошибка при обновлении имени канала: {e}")
        self.channel_counter = len(channels) + 1

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        if interaction.component.custom_id not in ["limit", "rename", "kick"]:
            return
        if not interaction.author.voice:
            embed = make_embed(
                title="Ошибка",
                description="Вы должны находиться в голосовом канале!",
                color=ERROR_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        channel = interaction.author.voice.channel
        if not channel or channel.id not in self.voice_channels:
            embed = make_embed(
                title="Ошибка",
                description="Вы должны находиться в своём голосовом канале!",
                color=ERROR_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if self.voice_channels[channel.id] != interaction.author.id:
            embed = make_embed(
                title="Ошибка",
                description="Это не ваш канал!",
                color=ERROR_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if interaction.component.custom_id == "rename":
            modal = disnake.ui.Modal(
                title="Изменить название канала",
                custom_id="rename_modal",
                components=[
                    disnake.ui.TextInput(
                        label="Новое название",
                        custom_id="new_name",
                        style=disnake.TextInputStyle.short,
                        placeholder="Введите новое название канала",
                        required=True,
                        max_length=32
                    )
                ]
            )
            await interaction.response.send_modal(modal)
        elif interaction.component.custom_id == "limit":
            modal = disnake.ui.Modal(
                title="Изменить лимит участников",
                custom_id="limit_modal",
                components=[
                    disnake.ui.TextInput(
                        label="Новый лимит",
                        custom_id="new_limit",
                        style=disnake.TextInputStyle.short,
                        placeholder="Введите число от 0 до 99 (0 - без лимита)",
                        required=True,
                        max_length=2
                    )
                ]
            )
            await interaction.response.send_modal(modal)
        elif interaction.component.custom_id == "kick":
            modal = disnake.ui.Modal(
                title="Выгнать участника",
                custom_id="kick_modal",
                components=[
                    disnake.ui.TextInput(
                        label="Имя участника",
                        custom_id="user_name",
                        style=disnake.TextInputStyle.short,
                        placeholder="Введите имя участника для исключения",
                        required=True
                    )
                ]
            )
            await interaction.response.send_modal(modal)

    @commands.Cog.listener()
    async def on_modal_submit(self, interaction: disnake.ModalInteraction):
        if interaction.custom_id not in ["rename_modal", "limit_modal", "kick_modal"]:
            return
        if not interaction.author.voice:
            embed = make_embed(
                title="Ошибка",
                description="Вы должны находиться в голосовом канале!",
                color=ERROR_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        if interaction.custom_id == "rename_modal":
            new_name = interaction.text_values["new_name"]
            channel = interaction.author.voice.channel
            await channel.edit(name=f"{channel.name.split(':')[0]}: {new_name}")
            embed = make_embed(
                title="Успех",
                description="Название канала изменено!",
                color=INFO_COLOR
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        elif interaction.custom_id == "limit_modal":
            try:
                new_limit = int(interaction.text_values["new_limit"])
                if 0 <= new_limit <= 99:
                    channel = interaction.author.voice.channel
                    await channel.edit(user_limit=new_limit)
                    limit_text = "отключен" if new_limit == 0 else f"установлен на {new_limit}"
                    embed = make_embed(
                        title="Успех",
                        description=f"Лимит участников {limit_text}!",
                        color=INFO_COLOR
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                else:
                    embed = make_embed(
                        title="Ошибка",
                        description="Лимит должен быть от 0 до 99!",
                        color=ERROR_COLOR
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
            except ValueError:
                embed = make_embed(
                    title="Ошибка",
                    description="Пожалуйста, введите корректное число!",
                    color=ERROR_COLOR
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
        elif interaction.custom_id == "kick_modal":
            user_name = interaction.text_values["user_name"]
            channel = interaction.author.voice.channel
            member_to_kick = None
            for member in channel.members:
                if member.name.lower() == user_name.lower() or member.display_name.lower() == user_name.lower():
                    member_to_kick = member
                    break
            if member_to_kick:
                await member_to_kick.move_to(None)
                embed = make_embed(
                    title="Успех",
                    description=f"Участник {member_to_kick.display_name} был выгнан из канала!",
                    color=INFO_COLOR
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = make_embed(
                    title="Ошибка",
                    description="Участник не найден в канале!",
                    color=ERROR_COLOR
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(VoiceChannels(bot))