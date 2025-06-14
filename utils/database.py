import mysql.connector
import os
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger('sapphire_bot.database')

class Database:
    def __init__(self, host: str = "localhost", user: str = "botuser", password: str = "", database: str = "sapphirebot"):
        """Инициализация базы данных MySQL"""
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self._init_db()

    def _get_conn(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database,
            autocommit=True
        )

    def _init_db(self):
        """Инициализация структуры базы данных"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            # Создаем таблицу для уровней пользователей
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_levels (
                user_id VARCHAR(32) PRIMARY KEY,
                xp INT NOT NULL DEFAULT 0,
                level INT NOT NULL DEFAULT 0,
                last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                voice_seconds INT NOT NULL DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            # Создаем таблицу для сессий AI чата
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS ai_sessions (
                user_id VARCHAR(32) PRIMARY KEY,
                channel_id VARCHAR(32) NOT NULL,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            # Создаем таблицу для экономики
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_economy (
                user_id VARCHAR(32) PRIMARY KEY,
                balance INT NOT NULL DEFAULT 0
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            ''')
            logger.info("База данных MySQL успешно инициализирована")
        except Exception as e:
            logger.error(f"Ошибка при инициализации базы данных: {e}")
        finally:
            if 'conn' in locals():
                conn.close()

    def get_user_data(self, user_id: str) -> Dict[str, Any]:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT xp, level FROM user_levels WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return {"xp": result[0], "level": result[1]}
            return {"xp": 0, "level": 0}
        except Exception as e:
            logger.error(f"Ошибка при получении данных пользователя {user_id}: {e}")
            return {"xp": 0, "level": 0}
        finally:
            if 'conn' in locals():
                conn.close()

    def update_user_data(self, user_id: str, xp: int, level: int) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_levels (user_id, xp, level, last_message_time) VALUES (%s, %s, %s, CURRENT_TIMESTAMP) "
                "ON DUPLICATE KEY UPDATE xp=%s, level=%s, last_message_time=CURRENT_TIMESTAMP",
                (user_id, xp, level, xp, level)
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении данных пользователя {user_id}: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_top_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, xp, level FROM user_levels ORDER BY level DESC, xp DESC LIMIT %s",
                (limit,)
            )
            result = cursor.fetchall()
            return [{"user_id": row[0], "xp": row[1], "level": row[2]} for row in result]
        except Exception as e:
            logger.error(f"Ошибка при получении топа пользователей: {e}")
            return []
        finally:
            if 'conn' in locals():
                conn.close()

    def save_ai_session(self, user_id: str, channel_id: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ai_sessions (user_id, channel_id, last_interaction) VALUES (%s, %s, CURRENT_TIMESTAMP) "
                "ON DUPLICATE KEY UPDATE channel_id=%s, last_interaction=CURRENT_TIMESTAMP",
                (user_id, channel_id, channel_id)
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении сессии AI для пользователя {user_id}: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_ai_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT channel_id, last_interaction FROM ai_sessions WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                return {"channel_id": result[0], "last_interaction": result[1]}
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении сессии AI для пользователя {user_id}: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def delete_ai_session(self, user_id: str) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM ai_sessions WHERE user_id = %s", (user_id,))
            return True
        except Exception as e:
            logger.error(f"Ошибка при удалении сессии AI для пользователя {user_id}: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_user_balance(self, user_id: str) -> int:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM user_economy WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка при получении баланса пользователя {user_id}: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()

    def update_user_balance(self, user_id: str, balance: int) -> bool:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO user_economy (user_id, balance) VALUES (%s, %s) "
                "ON DUPLICATE KEY UPDATE balance=%s",
                (user_id, balance, balance)
            )
            return True
        except Exception as e:
            logger.error(f"Ошибка при обновлении баланса пользователя {user_id}: {e}")
            return False
        finally:
            if 'conn' in locals():
                conn.close()

    def get_user_voice_seconds(self, user_id: str) -> int:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT voice_seconds FROM user_levels WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Ошибка при получении voice_seconds пользователя {user_id}: {e}")
            return 0
        finally:
            if 'conn' in locals():
                conn.close()

    def add_user_voice_seconds(self, user_id: str, seconds: int) -> None:
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT voice_seconds FROM user_levels WHERE user_id = %s", (user_id,))
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
                    logger.info(f"Начислено {hours_gained * 10} SC пользователю {user_id} за {hours_gained} часов в войсе")
                except Exception as e:
                    logger.error(f"Ошибка при начислении SC за голосовую активность: {e}")
            cursor.execute(
                "UPDATE user_levels SET voice_seconds = %s WHERE user_id = %s",
                (new_value, user_id)
            )
            logger.info(f"Обновлено время в войсе для пользователя {user_id}: {current} -> {new_value} секунд")
        except Exception as e:
            logger.error(f"Ошибка при обновлении voice_seconds пользователя {user_id}: {e}")
        finally:
            if 'conn' in locals():
                conn.close()