import discord    # stable on 1.7.3
from discord.ext import tasks, commands
import os
import sqlite3
import time
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
                msg = await subscriber_channel.send("🫧"+str(cnt))
                # 天數釘選測試
                try:
                    pins = await subscriber_channel.pins()
                    for pinned in pins:
                            if pinned.content == "🫧"+str(cnt-1):
                                await pinned.unpin()
                    await msg.pin()
                except:
                    print("pinning failed")
                
            except:
                print(str(channel_id)+" has been deleted, skipping...")
                cur.execute(f"""DELETE FROM subscriptions
                WHERE channel_id={channel_id}""")
                con.commit()
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
        {artist.id}, '{artist_name}', 'none', "pfp/default.png", '#E4B8D6')""")
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
        try:
            channel = bot.get_channel(channel_id)
            await channel.send("The artist account has been closed.")
        except:
            print(str(channel_id)+" has been deleted, skipping...")
    cur.execute(f"DELETE FROM artists WHERE user_id={artist.id}")
    cur.execute(f"DELETE FROM subscriptions WHERE artist_id={artist.id}")
    con.commit()
    await artist_channel.send("The artist account has been closed.")


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
async def unsubscribe(ctx):
    channel = ctx.channel
    cur.execute(f"""DELETE FROM subscriptions
    WHERE channel_id={channel.id}""")
    con.commit()
    await channel.send("unsubscribed")


@bot.command(pass_context=True)
async def change_artist_name(ctx, new_name):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"""SELECT artist_name FROM artists
    WHERE user_id={artist.id}""")
    old_name = res.fetchone()[0]
    if old_name == None:
        await artist_channel.send("You are not an artist yet.")
    else:
        res = cur.execute(f"""SELECT channel_id FROM subscriptions
        WHERE artist_id={artist.id}""")
        channel_ids = res.fetchall()
        for channel_id in channel_ids:
            channel = bot.get_channel(channel_id[0])
            msg = old_name+" have changed their name to "+new_name+"!"
            try:
                await channel.send(msg)
            except:
                print("Deleting "+str(channel_id))
                cur.execute(f"""DELETE FROM subscriptions
                WHERE channel_id={channel_id}""")
                con.commit()
        cur.execute(f"""UPDATE artists
        SET artist_name='{new_name}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Artist\'s name changed!")


@bot.command(pass_context=True)
async def change_artist_color(ctx, color_code):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"""SELECT artist_name FROM artists
    WHERE user_id={artist.id}""")
    artist_name = res.fetchone()[0]
    if artist_name == None:
        await artist_channel.send("You are not an artist yet.")
    else:
        res = cur.execute(f"""SELECT channel_id FROM subscriptions
        WHERE artist_id={artist.id}""")
        channel_ids = res.fetchall()
        for channel_id in channel_ids:
            channel = bot.get_channel(channel_id[0])
            msg = artist_name+" have changed their color to "+color_code+"!"
            try:
                await channel.send(msg)
            except Exception as e:
                print(e)
                #print("Deleting "+str(channel_id))
                #cur.execute(f"""DELETE FROM subscriptions
                #WHERE channel_id={channel_id}""")
                #con.commit()
        cur.execute(f"""UPDATE artists
        SET artist_color='{color_code}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Artist\'s color changed!")


@bot.command(pass_context=True)
async def change_description(ctx, description):
    artist = ctx.author
    artist_channel = ctx.channel
    res = cur.execute(f"""SELECT artist_name FROM artists
    WHERE user_id={artist.id}""")
    artist_name = res.fetchone()[0]
    if artist_name == None:
        await artist_channel.send("You are not an artist yet.")
    else:
        cur.execute(f"""UPDATE artists
        SET description='{description}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Description changed!")


@bot.command(pass_context=True)
async def change_pfp(ctx):
    artist = ctx.author
    artist_channel = ctx.channel
    attachments = ctx.message.attachments
    if len(attachments) == 0:
        await artist_channel.send("Please provide a picture.")
    else:
        res = cur.execute(f"""SELECT pfp_route FROM artists
        WHERE user_id={artist.id}""")
        old_route = res.fetchone()[0]
        print("deleting "+old_route)
        os.remove(old_route)
        fn = "pfp/"+str(time.time())+".png"
        await attachments[0].save(fn)
        cur.execute(f"""UPDATE artists
        SET pfp_route='{fn}' WHERE user_id={artist.id}""")
        con.commit()
        await artist_channel.send("Profile pic updated!")


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



# 暱稱更新區
@bot.command(pass_context=True)
async def change_nickname(ctx, nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE subscriptions
    SET nickname='{nickname}'
    WHERE channel_id={channel.id}""")
    con.commit()
    await channel.send("Nickname changed!")


@bot.command(pass_context=True)
async def change_artist_nickname(ctx, artist_nickname):
    channel = ctx.channel
    cur.execute(f"""UPDATE subscriptions
    SET artist_nickname='{artist_nickname}'
    WHERE channel_id={channel.id}""")
    con.commit()
    await channel.send("Artist\'s nickname changed!")


# 泡泡對話區
@bot.command(pass_context=True)
@commands.dm_only()
async def img(ctx):
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
        try:
            await channel.send(files=[await f.to_file() for f in attachments])
        except Exception as e:
            print(e)
            #cur.execute(f"""DELETE FROM subscriptions
            #WHERE channel_id={channel_id}""")
            #con.commit()


@bot.command(pass_context=True)
@commands.dm_only()
async def bbl(ctx, text):
    artist = ctx.author
    artist_channel = await artist.create_dm()

    res = cur.execute(f"""SELECT * FROM artists
    WHERE user_id={artist.id}""")
    values = res.fetchone()
    artist_name = values[1]

    pfp_route = values[3]
    if pfp_route is None:
        pfp_route = "pfp/default.png"

    artist_color = values[4]
    try:
        color = discord.Color.from_str(artist_color)
    except:
        color = discord.Color.from_str("#E4B8D6")
    description = values[5]


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
        display_name = "("+artist_name+")"+artist_nickname+": "
        embed = discord.Embed(title=text.replace("y/n", nickname),
                             color=color)
        embed.set_author(name=display_name, icon_url="attachment://image.png")
        if description is not None:
            embed.set_footer(text=description)
        try:
            file = discord.File(pfp_route, filename="image.png")
            await channel.send(file=file, embed=embed)
        except Exception as e:
            print(e)
            #cur.execute(f"""DELETE FROM subscriptions
            #WHERE channel_id={channel_id}""")
            #con.commit()


@bot.command(pass_context=True)
async def reply(ctx, text):
    channel = ctx.channel
    res = cur.execute(f"SELECT artist_id FROM subscriptions WHERE channel_id={channel.id}")
    try:
        artist_id = res.fetchone()[0]
        artist = await bot.fetch_user(artist_id)
        artist_channel = await artist.create_dm()
        await artist_channel.send(text)
    except:
        await channel.send("Sth's wrong! We can't find the artist...")


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
    await ctx.channel.send(len(values))
    await ctx.channel.send(values)


@bot.command(pass_context=True)
@commands.is_owner()
async def add_column(ctx):
    cur.execute(f"""ALTER TABLE artists
    ADD description TEXT""")
    con.commit()
    await ctx.channel.send("done!")


@bot.command(pass_context=True)
@commands.is_owner()
async def server_cnt(ctx):
    n = len(bot.guilds)
    bar = "["
    for i in range(0, n):
        bar += "\|"
    for i in range(n, 75):
        bar += " "
    bar += "]"+str(n)+"/75"
    await ctx.channel.send(bar)


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
