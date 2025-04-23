import disnake
from disnake.ext import commands

class VoiceChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_channels = {}  # Словарь для хранения информации о каналах
        self.channel_counter = 1  # Счетчик для нумерации каналов
        self.settings_message = None  # Сообщение с настройками

    async def create_settings_message(self, guild):
        """Создает сообщение с настройками в канале Voice Settings"""
        settings_channel = disnake.utils.get(guild.text_channels, name="💽・voice-settings")
        if not settings_channel:
            settings_channel = await guild.create_text_channel("💽・voice-settings")
        else:
            # Очищаем все предыдущие сообщения в канале
            await settings_channel.purge()

        embed = disnake.Embed(
            title="Настройки голосового канала",
            description=(
                "Измените конфигурацию вашей комнаты с помощью панели управления.\n\n"
                "<:Sapphire__icon:1159785635628994601> - Изменить название\n"
                "<:Sapphire_icon:1159785674929623210> - Изменить количество участников\n"
                "<:Sapphire_icon:1159787647712120924> - Выгнать участника"
            ),
            color=disnake.Color.blue()
        ).set_image(
            url="https://cdn.discordapp.com/attachments/1079626559423512679/1098117546328195072/whiteline.gif"
        ).set_footer(
            text="С уважением, администрация Sapphire Creators💎"
        )

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
            # Добавляем проверку на системный канал
            if after.channel and after.channel.name == "「🔑」Create a voice" and after.channel.id not in self.voice_channels:
                existing_channel = next((channel for channel, owner_id in self.voice_channels.items() 
                                      if owner_id == member.id), None)
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
                
                await new_channel.set_permissions(member, connect=True, manage_channels=True, 
                                               mute_members=True, deafen_members=True)
                await new_channel.set_permissions(member.guild.default_role, connect=True)
                
                await member.move_to(new_channel)
                self.voice_channels[new_channel.id] = member.id
                self.channel_counter += 1

            if before.channel and before.channel.id in self.voice_channels:
                if len(before.channel.members) == 0:
                    await before.channel.delete()
                    del self.voice_channels[before.channel.id]
                    await self.update_channel_numbers(before.channel.guild)

        except Exception as e:
            print(f"Произошла ошибка: {e}")

    @commands.Cog.listener()
    async def update_channel_numbers(self, guild):
        """Обновляет номера каналов после удаления"""
        channels = sorted(
            [(channel_id, channel) for channel_id, owner_id in self.voice_channels.items()
             if (channel := guild.get_channel(channel_id)) is not None],
            key=lambda x: x[1].position
        )
        
        for i, (channel_id, channel) in enumerate(channels, 1):
            try:
                current_name = channel.name
                new_name = f"{i}: {current_name.split(':', 1)[1].strip()}"
                await channel.edit(name=new_name)
            except Exception as e:
                print(f"Ошибка при обновлении имени канала: {e}")
        
        self.channel_counter = len(channels) + 1

    @commands.Cog.listener()
    async def on_button_click(self, interaction: disnake.MessageInteraction):
        if not interaction.component.custom_id in ["limit", "rename", "kick"]:
            return

        if not interaction.author.voice:
            await interaction.response.send_message("Вы должны находиться в голосовом канале!", ephemeral=True)
            return

        channel = interaction.author.voice.channel
        if not channel or channel.id not in self.voice_channels:
            await interaction.response.send_message("Вы должны находиться в своём голосовом канале!", ephemeral=True)
            return

        if self.voice_channels[channel.id] != interaction.author.id:
            await interaction.response.send_message("Это не ваш канал!", ephemeral=True)
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
        elif interaction.component.custom_id == "lock":
            is_locked = not channel.permissions_for(interaction.guild.default_role).connect
            await channel.set_permissions(interaction.guild.default_role, connect=not is_locked)
            status = "приватным" if not is_locked else "публичным"
            await interaction.response.send_message(f"Канал стал {status}!", ephemeral=True)
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
        # Проверяем тип модального окна по custom_id
        if not interaction.custom_id in ["rename_modal", "limit_modal", "kick_modal"]:
            return
    
        if not interaction.author.voice:
            await interaction.response.send_message("Вы должны находиться в голосовом канале!", ephemeral=True)
            return

        if interaction.custom_id == "rename_modal":
            new_name = interaction.text_values["new_name"]
            channel = interaction.author.voice.channel
            await channel.edit(name=f"{channel.name.split(':')[0]}: {new_name}")
            await interaction.response.send_message("Название канала изменено!", ephemeral=True)
        elif interaction.custom_id == "limit_modal":
            try:
                new_limit = int(interaction.text_values["new_limit"])
                if 0 <= new_limit <= 99:
                    channel = interaction.author.voice.channel
                    await channel.edit(user_limit=new_limit)
                    limit_text = "отключен" if new_limit == 0 else f"установлен на {new_limit}"
                    await interaction.response.send_message(f"Лимит участников {limit_text}!", ephemeral=True)
                else:
                    await interaction.response.send_message("Лимит должен быть от 0 до 99!", ephemeral=True)
            except ValueError:
                await interaction.response.send_message("Пожалуйста, введите корректное число!", ephemeral=True)
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
                await interaction.response.send_message(f"Участник {member_to_kick.display_name} был выгнан из канала!", ephemeral=True)
            else:
                await interaction.response.send_message("Участник не найден в канале!", ephemeral=True)

def setup(bot):
    bot.add_cog(VoiceChannels(bot))