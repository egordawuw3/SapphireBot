import disnake
from config.constants import STAFF_ROLE_ID, ERROR_COLOR
from utils.embed_utils import make_embed
from functools import wraps

async def is_staff(inter: disnake.ApplicationCommandInteraction) -> bool:
    staff_role = inter.guild.get_role(STAFF_ROLE_ID)
    return staff_role in inter.author.roles if staff_role else False

def require_staff():
    def decorator(func):
        @wraps(func)
        async def wrapper(self, inter: disnake.ApplicationCommandInteraction, *args, **kwargs):
            if not await is_staff(inter):
                embed = make_embed(
                    title="Ошибка доступа",
                    description="У вас недостаточно прав для использования этой команды.",
                    color=ERROR_COLOR
                )
                await inter.response.send_message(embed=embed, ephemeral=True)
                return
            return await func(self, inter, *args, **kwargs)
        return wrapper
    return decorator 