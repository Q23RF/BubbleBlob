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



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content == "!inc":
        res = cur.execute("SELECT * FROM subscriptions")
        values = res.fetchall()
        for v in values:
            channel_id = v[0]
            artist_id = v[1]
            cnt = v[2]
            subscriber_channel = bot.get_channel(channel_id)
            try:
                await subscriber_channel.send("🫧"+str(cnt))
            except:
                print(str(channel_id)+" has been deleted, skipping...")
        cur.execute("UPDATE subscriptions SET cnt=cnt+1")
        con.commit()
        await message.channel.send("++")
    await bot.process_commands(message)

# 帳號設定區
@bot.command(pass_context=True)
async def init(ctx, artist_name):
    artist = ctx.author
    artist_channel = ctx.channel
    try:
        cur.execute(f"""INSERT INTO artists VALUES (
        {artist.id}, '{artist_name}', 'none')""")
        con.commit()
        await artist_channel.send("You have successfully registered as an artist!")
    except:
        await artist_channel.send("Registration failed.")


@bot.command(pass_context=True)
async def close(ctx, artist_name):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"SELECT channel_id FROM subscriptions WHERE artist_id={artist.id}")
    channel_ids = res.fetchall()
    for channel_id in channel_ids:
        channel = bot.get_channel(channel_id)
        await channel.send("The artist account has been closed.")
    cur.execute(f"DELETE FROM artists WHERE user_id={artist.id}")
    cur.execute(f"DELETE FROM subscriptions WHERE artist_id={artist.id}")
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
    try:
        res = cur.execute(f"SELECT user_id FROM artists WHERE artist_name='{artist_name}'")
        artist_id = res.fetchone()[0]
        if artist_id is None:
            await channel.send("sth's wrong! We can't find the artist...")
            return
        artist = await bot.fetch_user(artist_id)
        artist_channel = await artist.create_dm()
        cur.execute(f"""INSERT INTO subscriptions VALUES
        ({channel.id}, {artist.id}, 0, '{nickname}', 'none')""")
        con.commit()
        res = cur.execute(f"SELECT welcome FROM artists WHERE user_id={artist_id}")
        welcome = res.fetchone()[0]
        welcome = welcome.replace("y/n", nickname)
        if welcome == "none":
            await channel.send("This channel have subscribed to "+artist_name+"\'s bubble!")
        else:
            await channel.send(welcome)
        await artist_channel.send("You have a new subscriber!")
    except:
        await channel.send("Subscription failed.")

@bot.command(pass_context=True)
async def unsubscribe(ctx, artist_name):
    channel = ctx.channel
    cur.execute(f"""DELETE FROM subscriptions
    WHERE channel_id={channel.id}""")
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
            try:
                id = s[0]
                nickname = s[1]
                channel = bot.get_channel(id)
                msg = s[1]+", "+old_name+" have changed their name to "+new_name+"!"
                await channel.send(msg)
            except:
                continue
        cur.execute(f"""ALTER TABLE {old_name}
        RENAME TO {new_name};""")
        cur.execute(f"""UPDATE artists
        SET artist_name='{new_name}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Artist\'s name changed!")


# 暱稱更新區
@bot.command(pass_context=True)
async def change_nickname(ctx, nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE subscriptions
    SET nickname='{nickname}'
    WHERE channel_id={channel.id}""")
    con.commit()
    await channel.send("nickname changed!")


@bot.command(pass_context=True)
async def change_artist_nickname(ctx, artist_nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE subscriptions
    SET artist_nickname='{artist_nickname}'
    WHERE channel_id={channel.id}""")
    con.commit()
    await channel.send("artist\'s nickname changed!")


# 泡泡對話區
@bot.command(pass_context=True)
async def bbl(ctx, text):
    attachments = ctx.message.attachments
    artist = ctx.author
    artist_channel = await artist.create_dm()
    res = cur.execute(f"""SELECT artist_name FROM artists
    WHERE user_id={artist.id}""")
    artist_name = res.fetchone()[0]
    res = cur.execute(f"""SELECT * FROM subscriptions
    WHERE artist_id={artist.id}""")
    subscription = res.fetchall()
    for s in subscription:
        channel_id = s[0]
        nickname = s[3]
        artist_nickname = s[4]
        if artist_nickname == "none":
            artist_nickname = artist_name
        channel = bot.get_channel(channel_id)
        msg = "("+artist_name+")"+artist_nickname+": "+text.replace("y/n", nickname)
        try:
            await channel.send(msg, files=[await f.to_file() for f in attachments])
        except:
            print(str(channel_id)+" failed to receive bbl from "+artist_name)

@bot.command(pass_context=True)
async def reply(ctx, text):
    channel = ctx.channel
    res = cur.execute(f"SELECT artist_id FROM subscriptions WHERE channel_id={channel.id}")
    artist_id = res.fetchone()[0]
    if artist_id is None:
        await channel.send("sth's wrong! We can't find the artist...")
        return
    artist = await bot.fetch_user(artist_id)
    artist_channel = await artist.create_dm()
    await artist_channel.send(text)

# 輔助指令區
@bot.command()
async def submit(ctx, msg):
    attachments = ctx.message.attachments
    channel = bot.get_channel(1140266438364512346)
    await channel.send("投稿:" + msg, files=[await f.to_file() for f in attachments])
    return


@bot.command(pass_context=True)
async def get_all_artists(ctx):
    res = cur.execute(f"SELECT artist_name FROM artists")
    values = res.fetchall()
    await ctx.channel.send(values)


@bot.command(pass_context=True)
@commands.is_owner()
async def get_all_artists_data(ctx):
    res = cur.execute(f"SELECT * FROM artists")
    values = res.fetchall()
    await ctx.channel.send(values)


@bot.command(pass_context=True)
@commands.is_owner()
async def get_all_subscribers_data(ctx, aid):
    res = cur.execute(f"SELECT * FROM subscriptions WHERE artist_id={aid}")
    values = res.fetchall()
    await ctx.channel.send(values)


@bot.command(pass_context=True)
@commands.is_owner()
async def reset_cnt(ctx):
    cur.execute(f"""UPDATE subscriptions
    SET cnt=0""")
    con.commit()
    await ctx.channel.send("done!")


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
