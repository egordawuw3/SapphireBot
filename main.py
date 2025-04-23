import os
import disnake
from disnake.ext import commands
from dotenv import load_dotenv
from http.server import HTTPServer, BaseHTTPRequestHandler

load_dotenv()

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')
        
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

intents = disnake.Intents.all()
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    test_guilds=[832291503581167636],
    command_sync_flags=commands.CommandSyncFlags.default()  # Заменяем sync_commands
)

@bot.event
async def on_ready():
    print("Бот готов к работе!")
    try:
        # Устанавливаем статус точно как на скриншоте
        await bot.change_presence(
            activity=disnake.Activity(
                type=disnake.ActivityType.watching,
                name="Sapphire Creators | Творите и учитесь! 🎓"
            ),
            status=disnake.Status.online
        )
        print("Статус бота успешно установлен")
    except Exception as e:
        print(f"Ошибка при установке статуса: {e}")

for file in os.listdir("./cogs"):
    if file.endswith(".py"):
        extension_name = f"cogs.{file[:-3]}"  # Используем правильное имя файла без .py
        try:
            bot.load_extension(extension_name)
            print(f"Загружено расширение: {extension_name}")
        except Exception as e:
            print(f"Не удалось загрузить расширение {extension_name}: {str(e)}")

def run_server():
    try:
        port = int(os.getenv('PORT', 10000))
        server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
        print(f"HTTP сервер запущен на порту {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Ошибка сервера: {e}")

if __name__ == "__main__":
    try:
        # Запускаем HTTP сервер в отдельном потоке
        import threading
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        
        # Запускаем бота
        token = os.getenv('DISCORD_TOKEN')  # Получаем токен из .env файла
        if not token:
            raise ValueError("Токен Discord не найден в переменных окружения")
        
        print("Запуск бота...")
        bot.run(token)
    except Exception as e:
        print(f"Ошибка: {e}")