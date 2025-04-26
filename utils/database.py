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
                last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        """Обновить данные пользователя"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT OR REPLACE INTO user_levels (user_id, xp, level, last_message_time) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                (user_id, xp, level)
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