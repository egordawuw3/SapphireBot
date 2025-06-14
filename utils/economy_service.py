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

async def get_top_balances(limit: int = 10) -> list[tuple[str, int]]:
    """
    Получить топ пользователей по балансу.
    Возвращает список кортежей (user_id, balance), отсортированных по убыванию баланса.
    """
    balances = await load_all_balances()  # {user_id: balance}
    top = sorted(balances.items(), key=lambda x: x[1], reverse=True)[:limit]
    return top

async def load_all_balances() -> dict:
    """
    Загружает все балансы пользователей из базы данных.
    Возвращает словарь {user_id: balance}.
    """
    try:
        data = db._read_json(db.economy_file)
        return data
    except Exception as e:
        import logging
        logging.getLogger('sapphire_bot.database').error(f"Ошибка при загрузке всех балансов: {e}")
        return {} 