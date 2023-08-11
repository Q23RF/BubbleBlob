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
async def init(ctx, artist_name):
    artist = ctx.author
    cur.execute(f"""CREATE TABLE {artist_name} (
    user_id INTEGER UNIQUE,
    nickname TEXT
    )""")
    cur.execute(f"""INSERT INTO artists VALUES (
    {artist.id}, '{artist_name}')""")
    con.commit()
    artist_channel = await artist.create_dm()
    await artist_channel.send("You have successfully registered as an artist!")


@bot.command(pass_context=True)
async def subscribe(ctx, artist_name, nickname):
    subscriber = ctx.author
    subscriber_channel = await subscriber.create_dm()
    res = cur.execute(f"SELECT user_id FROM artists WHERE artist_name='{artist_name}'")
    artist_id = res.fetchone()[0]
    if artist_id is None:
        await subscriber_channel.send("sth's wrong! We can't find the artist...")
        return
    artist = await bot.fetch_user(artist_id)
    print("adding "+subscriber.display_name+" to "+artist.display_name)
    cur.execute(f"INSERT INTO {artist_name} VALUES ({subscriber.id}, '{nickname}')")
    con.commit()
    await subscriber_channel.send("You have subscribed to "+artist_name+"\'s bubble!")


@bot.command(pass_context=True)
async def bbl(ctx, text):
    artist = ctx.author
    artist_channel = await artist.create_dm()
    res = cur.execute(f"SELECT artist_name FROM artists WHERE user_id={artist.id}")
    artist_name = res.fetchone()[0]
    if artist_name is None:
        await artist_channel.send("You\'re not an artist yet.")
        return
    res = cur.execute(f"SELECT * FROM {artist_name}")
    subscribers = res.fetchall()
    for s in subscribers:
        user_id = s[0]
        nickname = s[1]
        subscriber = await bot.fetch_user(user_id)
        dm_channel = await subscriber.create_dm()
        await dm_channel.send(artist_name+": "+text.replace("y/n", nickname))

@bot.command(pass_context=True)
async def reply(ctx, artist_name, text):
    subscriber = ctx.author
    subscriber_channel = await subscriber.create_dm()
    res = cur.execute(f"SELECT user_id FROM artists WHERE artist_name='{artist_name}'")
    artist_id = res.fetchone()[0]
    if artist_id is None:
        await subscriber_channel.send("sth's wrong! We can't find the artist...")
        return
    artist = await bot.fetch_user(artist_id)
    artist_channel = await artist.create_dm()
    await artist_channel.send(text)
        

# 輔助指令區
@bot.command(pass_context=True)
async def get_all_artists(ctx):
    user = ctx.author
    user_channel = await user.create_dm()
    res = cur.execute(f"SELECT artist_name FROM artists")
    values = res.fetchall()
    await user_channel.send(values)


@bot.command(pass_context=True)
async def get_all_subscriber(ctx, aid):
    user = ctx.author
    user_channel = await user.create_dm()
    res = cur.execute(f"SELECT artist_name FROM artists WHERE user_id={aid}")
    artist_name = res.fetchone()[0]
    if artist_name is None:
        await user_channel.send("sth's wrong! We can't find the artist...")
    else:
        res = cur.execute(f"SELECT * FROM {artist_name}")
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
