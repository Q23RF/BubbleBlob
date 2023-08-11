import discord
from discord.ext import tasks, commands
import os
import sqlite3
from keep_alive import keep_alive

keep_alive()

con = sqlite3.connect("data.db")
cur = con.cursor()

bot = commands.Bot(command_prefix='!',
                   intents=discord.Intents.all())

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(pass_context=True)
async def dm(ctx):
    print("dming")
    user = bot.get_user(999328348562006026)
    dm_channel = await user.create_dm()
    await dm_channel.send("Ready")

@bot.command(pass_context=True)
async def subscribe(ctx, aid, nickname):
    subscriber = ctx.author
    artist = await bot.fetch_user(aid)
    subscriber_channel = await subscriber.create_dm()
    print("adding "+subscriber.display_name+" to "+artist.display_name)
    res = cur.execute(f"SELECT table_name FROM artists WHERE user_id={aid}")
    table_name = res.fetchone()[0]
    if table_name is None:
        await subscriber_channel.send("sth's wrong! We can't find the artist...")
        print("aid="+aid)
    else:
        cur.execute(f"INSERT INTO {table_name} VALUES ({subscriber.id}, '{nickname}')")
        con.commit()
       
        artist_channel = await artist.create_dm()
        #await artist_channel.send(nickname+f"({subscriber.display_name}) has subscribed to your Bubble!")
        await subscriber_channel.send("You have subscribed to "+artist.display_name+"\'s bubble!")

@bot.command(pass_context=True)
async def get_all_subscriber(ctx, aid):
    user = ctx.author
    user_channel = await user.create_dm()
    res = cur.execute(f"SELECT table_name FROM artists WHERE user_id={aid}")
    table_name = res.fetchone()[0]
    if table_name is None:
        await user_channel.send("sth's wrong! We can't find the artist...")
    else:
        res = cur.execute(f"SELECT * FROM {table_name}")
        values = res.fetchall()
        await user_channel.send(values)
    

try:
    bot.run(os.getenv("TOKEN"))
except discord.HTTPException as e:
    if e.status == 429:
        print(
            "The Discord servers denied the connection for making too many requests"
        )
        print(
            "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
        )
    else:
        raise e
