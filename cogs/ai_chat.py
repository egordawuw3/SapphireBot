import disnake
from disnake.ext import commands
import google.generativeai as genai
from datetime import datetime
import os
import logging
from typing import Dict, Optional
from utils.embed_utils import make_embed
from config.constants import INFO_COLOR, ERROR_COLOR, SUCCESS_COLOR

logger = logging.getLogger("sapphire_bot.ai_chat")

class UserSession:
    """Сессия пользователя для AI чата."""
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.last_interaction = datetime.now()
        self.message_count = 0
        self.history = []

class AiChat(commands.Cog):
    """Cog для приватного чата с ИИ (Gemini)."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._setup_gemini()
        self.user_sessions: Dict[int, UserSession] = {}

    def _setup_gemini(self) -> None:
        """Инициализация модели Gemini."""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                logger.error("API ключ Gemini не найден в переменных окружения")
                raise ValueError("API ключ Gemini не найден в переменных окружения")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                },
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                ]
            )
            logger.info("Модель gemini-1.5-flash успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации модели Gemini: {e}")
            self.model = None

    @commands.slash_command(
        name="ai",
        description="Создать приватный чат с ИИ"
    )
    async def ai_chat(self, inter: disnake.ApplicationCommandInteraction) -> None:
        """Создать приватный чат с ИИ в отдельной ветке."""
        try:
            for session in self.user_sessions.values():
                if session.channel_id == inter.channel.id:
                    embed = make_embed(
                        title="Ошибка",
                        description="В этом канале уже есть активный чат с ИИ!",
                        color=ERROR_COLOR
                    )
                    await inter.response.send_message(embed=embed, ephemeral=True)
                    return
            thread_name = f"ai-chat-{inter.author.name.lower()}"
            new_thread = await inter.channel.create_thread(
                name=thread_name,
                type=disnake.ChannelType.private_thread,
                reason=f"Приватный AI чат для {inter.author.display_name}",
                invitable=False
            )
            await new_thread.add_user(inter.author)
            self.user_sessions[inter.author.id] = UserSession(new_thread.id)
            embed = make_embed(
                title="✨ Приватный чат с ИИ создан",
                description=f"Ваша приватная ветка: {new_thread.mention}\nИспользуйте `/ask` для общения с ИИ",
                color=SUCCESS_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            welcome_embed = make_embed(
                title="👋 Добро пожаловать в приватный чат!",
                description="Используйте `/ask` для общения.",
                color=INFO_COLOR
            )
            await new_thread.send(embed=welcome_embed)
            logger.info(f"Создан новый чат с ИИ для пользователя {inter.author.id}")
        except Exception as e:
            logger.error(f"Ошибка при создании чата с ИИ: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Не удалось создать чат: {e}",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.slash_command(
        name="ask",
        description="Задать вопрос ИИ"
    )
    async def ask(
        self,
        inter: disnake.ApplicationCommandInteraction,
        question: str = commands.Param(description="Ваш вопрос")
    ) -> None:
        """Задать вопрос ИИ в приватной ветке."""
        if not isinstance(inter.channel, disnake.Thread) or not inter.channel.name.startswith("ai-chat-"):
            embed = make_embed(
                title="Ошибка",
                description="Эта команда доступна только в приватном чате с ИИ!",
                color=ERROR_COLOR
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            return
        try:
            await inter.response.defer()
            if self.model is None:
                embed = make_embed(
                    title="Ошибка",
                    description="Извините, но сервис ИИ временно недоступен. Попробуйте позже.",
                    color=ERROR_COLOR
                )
                await inter.followup.send(embed=embed, ephemeral=True)
                return
            user_session: Optional[UserSession] = None
            for user_id, session in self.user_sessions.items():
                if session.channel_id == inter.channel.id:
                    user_session = session
                    break
            if not user_session:
                user_session = UserSession(inter.channel.id)
                self.user_sessions[inter.author.id] = user_session
            user_session.last_interaction = datetime.now()
            user_session.message_count += 1
            user_session.history.append({"role": "user", "parts": [question]})
            try:
                chat = self.model.start_chat(history=user_session.history)
                response = await self.bot.loop.run_in_executor(
                    None,
                    lambda: chat.send_message(question).text
                )
                user_session.history.append({"role": "model", "parts": [response]})
                if len(user_session.history) > 20:
                    user_session.history = user_session.history[-20:]
                await inter.followup.send(response)
                logger.info(f"Отправлен ответ на вопрос пользователя {inter.author.id}")
            except Exception as e:
                if "safety" in str(e).lower():
                    embed = make_embed(
                        title="Запрос заблокирован",
                        description="Извините, но этот запрос был заблокирован системой безопасности.",
                        color=ERROR_COLOR
                    )
                    await inter.followup.send(embed=embed, ephemeral=True)
                    logger.warning(f"Запрос пользователя {inter.author.id} заблокирован системой безопасности: {question}")
                else:
                    embed = make_embed(
                        title="Ошибка",
                        description=f"Ошибка при генерации ответа: {e}",
                        color=ERROR_COLOR
                    )
                    await inter.followup.send(embed=embed, ephemeral=True)
                    logger.error(f"Ошибка при генерации ответа для пользователя {inter.author.id}: {e}")
        except Exception as e:
            logger.error(f"Общая ошибка в команде ask: {e}")
            embed = make_embed(
                title="Ошибка",
                description=f"Общая ошибка: {e}",
                color=ERROR_COLOR
            )
            await inter.followup.send(embed=embed, ephemeral=True)

def setup(bot: commands.Bot) -> None:
    bot.add_cog(AiChat(bot))