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


@skinport_client.listen("saleFeed")
async def on_sale_feed(data):
    paginator = commands.Paginator(prefix="", suffix="")
    salefeed = skinport.SaleFeed(data=data)
    sales = salefeed.sales
    for s in sales:
        if "\u2605" not in s.tags:
            return
        sales = await skinport_client.get_sales_history(s.market_hash_name)
        if sales[0].last_7_days.min is not None and sales[0].last_7_days.min > s.sale_price:
            paginator.add_line(f"{s.market_hash_name}: {s.sale_price} {s.currency} Float: {s.wear}\n<{s.url}>")
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(config.discord_webhook_url, session=session)
        for page in paginator.pages:
            await webhook.send(page)


if __name__ == "__main__":
    print("Running...")
    skinport_client.run()
