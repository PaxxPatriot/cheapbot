import sys

import aiohttp
import discord
import skinport
from discord.ext import commands

import config

if config.discord_webhook_url == '':
    print("You have to set a Discord Webhook URL in the config.py file", file=sys.stderr)
    sys.exit(1)

skinport_client = skinport.Client()

async def get_item_from_sales_history(market_hash_name: str) -> skinport.ItemWithSales:
    sales_history = await skinport_client.get_sales_history()
    return [item for item in sales_history if item.market_hash_name == market_hash_name][0]

@skinport_client.listen("saleFeed")
async def on_sale_feed(data):
    paginator = commands.Paginator(prefix="", suffix="")
    salefeed = skinport.SaleFeed(data=data)
    sales = salefeed.sales
    for s in sales:
        if s.suggested_price < 5: # Ignore items which are suggested for less than 5 EUR
            return

        if "\u2605" in s.tags and s.stattrak: # Ignore StatTrak Knives
            return
        
        item = await get_item_from_sales_history(s.market_hash_name)
        if not item:
            return

        if (item.last_7_days.avg is not None and item.last_7_days.avg > s.sale_price):
            paginator.add_line(f"{s.market_hash_name}: {s.sale_price} {s.currency} Float: {s.wear}\n<{s.url}>")

    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(config.discord_webhook_url, session=session)
        for page in paginator.pages:
            await webhook.send(page)


if __name__ == "__main__":
    print(f"Running... on skinport.py {skinport.__version__}")
    skinport_client.run()
