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