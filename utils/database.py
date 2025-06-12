import sqlite3
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('sapphire_bot.database')

class Database:
    def __init__(self, db_path: str = "data/sapphire.db"):
        """Инициализация базы данных"""
        # Создаем директорию для данных, если её нет
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Инициализация структуры базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Создаем таблицу для уровней пользователей
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id TEXT PRIMARY KEY,
                xp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 0,
                last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                voice_seconds INTEGER NOT NULL DEFAULT 0
            )
            ''')
            
            # Создаем таблицу для сессий AI чата
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_sessions (
                user_id TEXT PRIMARY KEY,
                channel_id TEXT NOT NULL,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Создаем таблицу для экономики
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_economy (
                user_id TEXT PRIMARY KEY,
                balance INTEGER NOT NULL DEFAULT 0
            )
            ''')
            
            conn.commit()
            logger.info("База данных успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
        finally:
            if conn:
                conn.close()
    
    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        """Получить данные пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT xp, level FROM user_levels WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {"xp": result[0], "level": result[1]}
            return {"xp": 0, "level": 0}
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            return {"xp": 0, "level": 0}
        finally:
            if conn:
                conn.close()
    
    def update_user_data(self, user_id: str, xp: int, level: int) -> bool:
        """Обновить данные пользователя (XP, level, last_message_time), не трогая voice_seconds"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE user_levels SET xp = ?, level = ?, last_message_time = CURRENT_TIMESTAMP WHERE user_id = ?",
                (xp, level, user_id)
            )
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных пользователя {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить топ пользователей по уровню и опыту"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT user_id, xp, level FROM user_levels ORDER BY level DESC, xp DESC LIMIT ?",
                (limit,)
            )
            result = cursor.fetchall()
            
            return [{"user_id": row[0], "xp": row[1], "level": row[2]} for row in result]
        except Exception as e:
            logger.error(f"Ошибка при получении топа пользователей: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def save_ai_session(self, user_id: str, channel_id: str) -> bool:
        """Сохранить сессию AI чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO ai_sessions (user_id, channel_id, last_interaction) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (user_id, channel_id)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении сессии AI для пользователя {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_ai_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Получить сессию AI чата пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT channel_id, last_interaction FROM ai_sessions WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result:
                return {"channel_id": result[0], "last_interaction": result[1]}
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении сессии AI для пользователя {user_id}: {e}")
            return None
        finally:
            if conn:
                conn.close()
    
    def delete_ai_session(self, user_id: str) -> bool:
        """Удалить сессию AI чата"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM ai_sessions WHERE user_id = ?", (user_id,))
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении сессии AI для пользователя {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_user_balance(self, user_id: str) -> int:
        """Получить баланс пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT balance FROM user_economy WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def update_user_balance(self, user_id: str, balance: int) -> bool:
        """Обновить баланс пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO user_economy (user_id, balance) VALUES (?, ?)",
                (user_id, balance)
            )
            
            conn.commit()
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}")
            return False
        finally:
            if conn:
                conn.close()
    
    def get_user_voice_seconds(self, user_id: str) -> int:
        """Получить общее время в войсе (секунды) пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT voice_seconds FROM user_levels WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка при получении voice_seconds пользователя {user_id}: {e}")
            return 0
        finally:
            if conn:
                conn.close()
    
    def add_user_voice_seconds(self, user_id: str, seconds: int) -> None:
        """Добавить секунды к общему времени в войсе пользователя и начислить SC за каждый новый полный час"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT voice_seconds FROM user_levels WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            current = result[0] if result else 0
            new_value = current + seconds
            # Начисление SC за каждый новый полный час
            old_hours = current // 3600
            new_hours = new_value // 3600
            hours_gained = new_hours - old_hours
            if hours_gained > 0:
                try:
                    from utils.economy_service import EconomyService
                    EconomyService.add_balance(user_id, hours_gained * 10)
                except Exception as e:
                    logger.error(f"Ошибка при начислении SC за голосовую активность: {e}")
            cursor.execute(
                "UPDATE user_levels SET voice_seconds = ? WHERE user_id = ?",
                (new_value, user_id)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Ошибка при обновлении voice_seconds пользователя {user_id}: {e}")
        finally:
            if conn:
                conn.close()