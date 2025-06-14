import json
import os
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger('sapphire_bot.database')

class Database:
    def __init__(self):
        """Инициализация базы данных JSON"""
        self.data_dir = "data"
        self.levels_file = os.path.join(self.data_dir, "levels.json")
        self.economy_file = os.path.join(self.data_dir, "economy.json")
        self._init_db()

    def _init_db(self):
        """Инициализация структуры базы данных"""
        try:
            # Создаем директорию для данных, если её нет
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)

            # Инициализируем файлы, если их нет
            if not os.path.exists(self.levels_file):
                with open(self.levels_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)

            if not os.path.exists(self.economy_file):
                with open(self.economy_file, 'w', encoding='utf-8') as f:
                    json.dump({}, f)

            logger.info("База данных JSON успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")

    def _read_json(self, file_path: str) -> Dict:
        """Чтение JSON файла"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Ошибка при чтении файла {file_path}: {e}")
            return {}

    def _write_json(self, file_path: str, data: Dict) -> bool:
        """Запись в JSON файл"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Ошибка при записи в файл {file_path}: {e}")
            return False

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        data = self._read_json(self.levels_file)
        user_data = data.get(user_id, {"xp": 0, "level": 0, "voice_seconds": 0})
        return {"xp": user_data.get("xp", 0), "level": user_data.get("level", 0)}

    def update_user_data(self, user_id: str, xp: int, level: int) -> bool:
        data = self._read_json(self.levels_file)
        if user_id not in data:
            data[user_id] = {"xp": 0, "level": 0, "voice_seconds": 0}
        data[user_id]["xp"] = xp
        data[user_id]["level"] = level
        data[user_id]["last_message_time"] = datetime.now().isoformat()
        return self._write_json(self.levels_file, data)

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        data = self._read_json(self.levels_file)
        users = [(user_id, user_data["xp"], user_data["level"]) 
                for user_id, user_data in data.items()]
        users.sort(key=lambda x: (x[2], x[1]), reverse=True)
        return [{"user_id": user[0], "xp": user[1], "level": user[2]} 
                for user in users[:limit]]

    def get_user_balance(self, user_id: str) -> int:
        data = self._read_json(self.economy_file)
        return data.get(user_id, 0)

    def update_user_balance(self, user_id: str, balance: int) -> bool:
        data = self._read_json(self.economy_file)
        data[user_id] = balance
        return self._write_json(self.economy_file, data)

    def get_user_voice_seconds(self, user_id: str) -> int:
        data = self._read_json(self.levels_file)
        return data.get(user_id, {}).get("voice_seconds", 0)

    def add_user_voice_seconds(self, user_id: str, seconds: int) -> None:
        try:
            data = self._read_json(self.levels_file)
            if user_id not in data:
                data[user_id] = {"xp": 0, "level": 0, "voice_seconds": 0}
            
            current = data[user_id].get("voice_seconds", 0)
            new_value = current + seconds
            
            # Начисление SC за каждый новый полный час
            old_hours = current // 3600
            new_hours = new_value // 3600
            hours_gained = new_hours - old_hours
            
            if hours_gained > 0:
                try:
                    from utils.economy_service import EconomyService
                    EconomyService.add_balance(user_id, hours_gained * 10)
                    logger.info(f"Начислено {hours_gained * 10} SC пользователю {user_id} за {hours_gained} часов в войсе")
                except Exception as e:
                    logger.error(f"Ошибка при начислении SC за голосовую активность: {e}")
            
            data[user_id]["voice_seconds"] = new_value
            self._write_json(self.levels_file, data)
            logger.info(f"Обновлено время в войсе для пользователя {user_id}: {current} -> {new_value} секунд")
        except Exception as e:
            logger.error(f"Ошибка при обновлении voice_seconds пользователя {user_id}: {e}")