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
    id INTEGER UNIQUE,
    nickname TEXT,
    artist_nickname TEXT DEFAULT 'none'
    )""")
    cur.execute(f"""INSERT INTO artists VALUES (
    {artist.id}, '{artist_name}', 'none')""")
    con.commit()
    artist_channel = await artist.create_dm()
    await artist_channel.send("You have successfully registered as an artist!")


@bot.command(pass_context=True)
async def close(ctx, artist_name):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"SELECT artist_name FROM artists WHERE user_id='{artist.id}'")
    name = res.fetchone()[0]
    if name != artist_name:
        await artist_channel.send("The artist name you entered doesn\'t match.")
    else:
        res = cur.execute(f"SELECT id FROM {artist_name}")
        subscriber_ids = res.fetchall()
        for sid in subscriber_ids:
            channel = bot.get_channel(sid)
            await channel.send(artist_name+" have closed their artist account.")
        cur.execute(f"DELETE FROM artists WHERE user_id={artist.id}")
        cur.execute(f"DROP TABLE {artist_name}")
        con.commit()
        await artist_channel.send("The artist account has been closed.")


@bot.command(pass_context=True)
async def set_welcome(ctx, welcome):
    artist = ctx.author
    channel = ctx.channel
    try:
        cur.execute(f"""UPDATE artists
        SET welcome='{welcome}' WHERE user_id={artist.id}""")
        con.commit()
        await channel.send("Welcome message updated!")
    except:
        await channel.send("Welcome message update failed.")


@bot.command(pass_context=True)
async def subscribe(ctx, artist_name, nickname):
    channel = ctx.channel
    res = cur.execute(f"SELECT user_id FROM artists WHERE artist_name='{artist_name}'")
    artist_id = res.fetchone()[0]
    if artist_id is None:
        await channel.send("sth's wrong! We can't find the artist...")
        return
    artist = await bot.fetch_user(artist_id)
    artist_channel = await artist.create_dm()
    cur.execute(f"INSERT INTO {artist_name} VALUES ({channel.id}, '{nickname}', 'none')")
    con.commit()
    res = cur.execute(f"SELECT welcome FROM artists WHERE user_id={artist_id}")
    welcome = res.fetchone()[0]
    welcome = welcome.replace("y/n", nickname)
    if welcome == "none":
        await channel.send("This channel have subscribed to "+artist_name+"\'s bubble!")
    else:
        await channel.send(welcome)
    await artist_channel.send("You have a new subscriber!")


@bot.command(pass_context=True)
async def unsubscribe(ctx, artist_name):
    channel = ctx.channel
    cur.execute(f"""DELETE FROM {artist_name}
    WHERE id={channel.id}""")
    con.commit()
    await channel.send("unsubscribed "+artist_name)


@bot.command(pass_context=True)
async def change_artist_name(ctx, new_name):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"""SELECT artist_name FROM artists
    WHERE user_id={artist.id}""")
    old_name = res.fetchone()[0]
    if old_name == None:
        await artist_channel.send("The artist name you entered doesn\'t match.")
    else:
        res = cur.execute(f"""SELECT * FROM {old_name}""")
        subscribers = res.fetchall()
        for s in subscribers:
            id = s[0]
            nickname = s[1]
            channel = bot.get_channel(id)
            msg = s[1]+", "+old_name+" have changed their name to "+new_name+"!"
            await channel.send(msg)
        cur.execute(f"""ALTER TABLE {old_name}
        RENAME TO {new_name};""")
        cur.execute(f"""UPDATE artists
        SET artist_name='{new_name}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Artist\'s name changed!")


@bot.command(pass_context=True)
async def change_nickname(ctx, artist_name, nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE {artist_name}
    SET nickname='{nickname}' WHERE id={channel.id}""")
    con.commit()
    await channel.send("nickname changed!")

@bot.command(pass_context=True)
async def change_artist_nickname(ctx, artist_name, artist_nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE {artist_name}
    SET artist_nickname='{artist_nickname}' WHERE id={channel.id}""")
    con.commit()
    await channel.send("artist\'s nickname changed!")

@bot.command(pass_context=True)
async def bbl(ctx, text):
    attachments = ctx.message.attachments
    for a in attachments:
        text += "\n" + a.url
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
        id = s[0]
        nickname = s[1]
        artist_nickname = s[2]
        if artist_nickname == "none":
            artist_nickname = artist_name
        channel = bot.get_channel(id)
        try:
            msg = "("+artist_name+")"+artist_nickname+": "+text.replace("y/n", nickname)
            await channel.send(msg)
        except:
            print(str(id)+" failed to receive bbl from "+artist_name)

@bot.command(pass_context=True)
async def reply(ctx, artist_name, text):
    channel = ctx.channel
    res = cur.execute(f"SELECT user_id FROM artists WHERE artist_name='{artist_name}'")
    artist_id = res.fetchone()[0]
    if artist_id is None:
        await channel.send("sth's wrong! We can't find the artist...")
        return
    artist = await bot.fetch_user(artist_id)
    artist_channel = await artist.create_dm()
    await artist_channel.send(text)
        

# 輔助指令區
@bot.command(pass_context=True)
async def get_all_artists(ctx):
    res = cur.execute(f"SELECT artist_name FROM artists")
    values = res.fetchall()
    await ctx.channel.send(values)


@bot.command(pass_context=True)
async def get_all_subscriber(ctx, aid):
    res = cur.execute(f"SELECT artist_name FROM artists WHERE user_id={aid}")
    artist_name = res.fetchone()[0]
    if artist_name is None:
        await ctx.channel.send("sth's wrong! We can't find the artist...")
    else:
        res = cur.execute(f"SELECT * FROM {artist_name}")
        values = res.fetchall()
        await ctx.channel.send(values)
    

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
