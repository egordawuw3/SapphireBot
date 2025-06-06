from utils.database import Database

db = Database()

class EconomyService:
    @staticmethod
    def get_balance(user_id: str) -> int:
        return db.get_user_balance(user_id)

    @staticmethod
    def set_balance(user_id: str, amount: int) -> None:
        db.update_user_balance(user_id, amount)

    @staticmethod
    def add_balance(user_id: str, amount: int) -> int:
        current = db.get_user_balance(user_id)
        new_balance = current + amount
        db.update_user_balance(user_id, new_balance)
        return new_balance

    @staticmethod
    def remove_balance(user_id: str, amount: int) -> int:
        current = db.get_user_balance(user_id)
        new_balance = max(0, current - amount)
        db.update_user_balance(user_id, new_balance)
        return new_balance

    @staticmethod
    def reset_balance(user_id: str) -> None:
        db.update_user_balance(user_id, 0)

async def get_top_balances(limit: int = 10) -> list[tuple[int, int]]:
    """
    Получить топ пользователей по балансу.
    Возвращает список кортежей (user_id, balance), отсортированных по убыванию баланса.
    """
    # Пример для словаря balances, адаптируй под свою БД
    balances = await load_all_balances()  # {user_id: balance}
    top = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top 

async def load_all_balances() -> dict:
    """
    Загружает все балансы пользователей из базы данных.
    Возвращает словарь {user_id: balance}.
    """
    import asyncio
    loop = asyncio.get_event_loop()
    def fetch():
        try:
            conn = db.db_path and __import__('sqlite3').connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, balance FROM user_economy")
            result = cursor.fetchall()
            return {row[0]: row[1] for row in result}
        except Exception as e:
            import logging
            logging.getLogger('sapphire_bot.database').error(f"Ошибка при загрузке всех балансов: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    return await loop.run_in_executor(None, fetch) 