import disnake
from disnake.ext import commands
import google.generativeai as genai
from datetime import datetime
import os
import logging
from typing import Dict, Optional

logger = logging.getLogger("sapphire_bot.ai_chat")

class UserSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.last_interaction = datetime.now()
        self.message_count = 0
        self.history = []

class AiChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._setup_gemini()
        self.user_sessions: Dict[int, UserSession] = {}
        
    def _setup_gemini(self) -> None:
        """Инициализация модели Gemini"""
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
    async def ai_chat(self, inter: disnake.ApplicationCommandInteraction):
        try:
            # Проверяем, есть ли уже активная сессия
            for session in self.user_sessions.values():
                if session.channel_id == inter.channel.id:
                    await inter.response.send_message(
                        "В этом канале уже есть активный чат с ИИ!",
                        ephemeral=True
                    )
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
            
            embed = disnake.Embed(
                title="✨ Приватный чат с ИИ создан",
                description=f"Ваша приватная ветка: {new_thread.mention}\n"
                          f"Используйте `/ask` для общения с ИИ",
                color=0x2ecc71
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
            
            welcome_embed = disnake.Embed(
                title="👋 Добро пожаловать в приватный чат!",
                description="Используйте `/ask` для общения.",
                color=0x3498db
            )
            await new_thread.send(embed=welcome_embed)
            logger.info(f"Создан новый чат с ИИ для пользователя {inter.author.id}")
            
        except Exception as e:
            logger.error(f"Ошибка при создании чата с ИИ: {e}")
            embed = disnake.Embed(
                title="❌ Ошибка",
                description=f"Не удалось создать чат: {str(e)}",
                color=0xff0000
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
    ):
        if not isinstance(inter.channel, disnake.Thread) or not inter.channel.name.startswith("ai-chat-"):
            return await inter.response.send_message(
                "Эта команда доступна только в приватном чате с ИИ!", 
                ephemeral=True
            )
            
        try:
            await inter.response.defer()
            
            if self.model is None:
                await inter.followup.send("Извините, но сервис ИИ временно недоступен. Попробуйте позже.", ephemeral=True)
                return
                
            # Находим сессию пользователя
            user_session = None
            for user_id, session in self.user_sessions.items():
                if session.channel_id == inter.channel.id:
                    user_session = session
                    break
                    
            if not user_session:
                # Создаем новую сессию, если не найдена
                user_session = UserSession(inter.channel.id)
                self.user_sessions[inter.author.id] = user_session
                
            # Обновляем время последнего взаимодействия
            user_session.last_interaction = datetime.now()
            user_session.message_count += 1
            
            # Добавляем вопрос в историю
            user_session.history.append({"role": "user", "parts": [question]})
                
            try:
                # Используем историю сообщений для контекста
                chat = self.model.start_chat(history=user_session.history)
                response = await self.bot.loop.run_in_executor(
                    None,
                    lambda: chat.send_message(question).text
                )
                
                # Добавляем ответ в историю
                user_session.history.append({"role": "model", "parts": [response]})
                
                # Ограничиваем историю до последних 10 сообщений
                if len(user_session.history) > 20:
                    user_session.history = user_session.history[-20:]
                    
                await inter.followup.send(response)
                logger.info(f"Отправлен ответ на вопрос пользователя {inter.author.id}")
                
            except Exception as e:
                if "safety" in str(e).lower():
                    await inter.followup.send("Извините, но этот запрос был заблокирован системой безопасности.", ephemeral=True)
                    logger.warning(f"Запрос пользователя {inter.author.id} заблокирован системой безопасности: {question}")
                else:
                    await inter.followup.send(f"Ошибка при генерации ответа: {str(e)}", ephemeral=True)
                    logger.error(f"Ошибка при генерации ответа для пользователя {inter.author.id}: {e}")
                
        except Exception as e:
            logger.error(f"Общая ошибка в команде ask: {e}")
            await inter.followup.send(f"Общая ошибка: {str(e)}", ephemeral=True)

def setup(bot):
    bot.add_cog(AiChat(bot))