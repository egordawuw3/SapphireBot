import disnake
from datetime import datetime
from config.constants import FOOTER_TEXT

def make_embed(title: str, description: str = None, color: int = 0x2B65EC, fields=None, thumbnail=None, image=None) -> disnake.Embed:
    embed = disnake.Embed(title=title, description=description, color=color, timestamp=datetime.now())
    embed.set_footer(text=FOOTER_TEXT)
    if fields:
        for field in fields:
            embed.add_field(**field)
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    if image:
        embed.set_image(url=image)
    return embed 