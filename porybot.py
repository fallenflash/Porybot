"""A Work in progress bot to do somethings i thought were cool around discord

Returns:
    code -- returns the users pogo friend code from discord
        may be used by its self to call your own, or followed by a name to call theirs

    setcode -- to initially set friend code

    silph -- brings back a mockup of the silph league trainer card
        may be used by its self to call your own, or followed by a name to call theirs

    setsilph -- used to set name on silphcard if different from discord
        usercase "setsilph fallenflash"

    setloc -- to set location if you want to use something other than silph provides
        usecase "setloc Virginia Beach, Va"  (accepts any string)

    directions -- returns directions to a gym in a monocle db. (working on rocketmap for future)
        usecase "directions find shiny deals at sprint"

    All user and gym names are run through a fuzzy sting matcher, so approximations and misspellings will be accepted

"""


import argparse
import asyncio
import json
import logging
import os
import platform
import random
import re
import sys
import types
from datetime import datetime, timedelta
import requests
import discord
from discord.ext import commands
from discord.ext.commands import Bot

from pokemonlist import emojis, pokejson

try:
    from fuzzywuzzy import fuzz
    from fuzzywuzzy import process
except ImportError:
    print('please install fuzzywuzzy')
    print('python3 -m pip install fuzzywuzzy[speedup]')
    sys.exit(3)


try:
    import MySQLdb
except ImportError:
    print('Please install mysqlclient')
    print('Linux: $ sudo pip install mysqlclient')
    sys.exit(3)
try:
    import yaml
except ImportError:
    print('Please install pyyaml')
    print('Linux $ sudo pip install pyyaml')
    sys.exit(3)


def main(args, loglevel):
    logging.basicConfig(format="%(levelname)s: %(message)s", level=loglevel)

    bot_config_file = os.path.join(os.path.dirname(__file__), 'config.yml')

    with open(bot_config_file, "r") as c_file:
        bot_config = yaml.load(c_file)


    # Open database connection
    try:
        database = MySQLdb.connect(
            bot_config['mysql']['host'],
            bot_config['mysql']['user'],
            bot_config['mysql']['password'],
            bot_config['mysql']['database']
        )
    except MySQLdb.Error as err:
        sys.stderr.write("[ERROR] {}: {}\n".format(err.args[0], err.args[1]))
        sys.exit(3)
    else:
        # Prepare a cursor object using cursor() method
        cursor = database.cursor()
    # x2 for bot database
    try:
        database2 = MySQLdb.connect(
            bot_config['mysql']['host'],
            bot_config['mysql']['user'],
            bot_config['mysql']['password'],
            bot_config['mysql']['database2']
        )
    except MySQLdb.Error as err:
        sys.stderr.write("[ERROR] {}: {}\n".format(err.args[0], err.args[1]))
        sys.exit(3)
    else:
        # Prepare a cursor object using cursor() method
        cursor2 = database2.cursor()
    try:
        cursor2.execute(
            "CREATE TABLE IF NOT EXISTS `users` ("
	        "`Id` VARCHAR(20) NOT NULL,"
            "`Username` VARCHAR(50) NOT NULL,"
            "`Friend_Code` VARCHAR(12) NOT NULL DEFAULT 'x',"
            "`Silph_Name` VARCHAR(50) NULL DEFAULT NULL,"
            "`Location` VARCHAR(50) NULL DEFAULT NULL,"
            "PRIMARY KEY (`Id`),"
            "UNIQUE INDEX `Id` (`Id`)"
            ")"
            "COLLATE='latin1_swedish_ci'"
            "ENGINE=InnoDB;"
                    )
        database2.ping()
        database2.commit()
    except MySQLdb.Error as err:
        sys.stderr.write("[ERROR] {}: {}\n".format(err.args[0], err.args[1]))


    bot = Bot(description=bot_config['description'],command_prefix=bot_config['command_prefix'], pm_help=bot_config['pm_help'])


    # This is what happens everytime the bot launches. In this case, it prints information like server count, user count the bot is connected to, and the bot id in the console.
    # caution in changing it as it may cause malfunctions with the bot
    @bot.event
    async def on_ready():
        print('Logged in as '+bot.user.name+' (ID:'+bot.user.id+') | Connected to ' +
              str(len(bot.servers))+' servers | Connected to '+str(len(set(bot.get_all_members())))+' users')
        print('--------')
        print('Current Discord.py Version: {} | Current Python Version: {}'.format(
            discord.__version__, platform.python_version()))
        print('--------')
        print('Use this link to invite {}:'.format(bot.user.name))
        print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(bot.user.id))
        print('--------')
        print('Admin/Owners: {}'.format(str(bot_config['privileged_ids'])))
        print('--------')
        print('You are running Porybot v0.2')
        return await bot.change_presence(game=discord.Game(name='Doing Robot Things'))

    def find_pokemon_id(name):
        if name == 'Nidoran-F':
            return 29
        elif name == 'Nidoran-M':
            return 32
        elif name == 'Mr-Mime':
            return 122
        elif name == 'Ho-Oh':
            return 250
        elif name == 'Mime-Jr':
            return 439
        else:
            name = name.split('-')[0]
            for key in pokejson.keys():
                value = pokejson[key]
                if value == name:
                    return int(key)
            return 0

    def find_badges(badges):
        badgelist = []
        for badge in badges:
            if bot_config['badgeserver']:
                try:
                    name = badge['Badge']['slug']
                    name = name.replace('-', '')
                    emoji = emojis[f'{name}']
                    badgelist.append(emoji)
                except:
                    emoji = f"\[{badge['Badge']['name']}\]\({badge['Badge']['image']}\)"
                    badgelist.append(str(emoji))
            else:
                emoji = f"\[{badge['Badge']['name']}\]\({badge['Badge']['image']}\)"
                badgelist.append(str(emoji))
        return badgelist

    def find_memberb(ctx, maybe):
        guild = ctx.message.server.members
        cursor2.execute("SELECT username FROM users")
        dbn = cursor2.fetchall()
        guildlist = []
        for a in dbn:
            b = a[0]
            c = re.sub('#[0-9]{4}', '', b)
            guildlist.append(c)
        results = process.extractOne(
            maybe, guildlist, scorer=fuzz.partial_ratio)
        user = discord.utils.get(guild, name=results[0])
        return user

    def find_member(ctx, maybe):
        guild = ctx.message.server.members
        guildlist = []
        for member in guild:
            displayname = member.display_name
            name = member.name
            guildlist.append(displayname)
            guildlist.append(name)
        results = process.extractOne(
            maybe, guildlist, scorer=fuzz.partial_ratio)
        user = discord.utils.get(guild, name=results[0])
        return user

    def find_pokemon_name(number):
        for k, v in pokejson.items():
            if k == number:
                return str(v)

    def find_party(names):
        party = []
        for number in names:
            if number != 0:
                mon = pokejson[f"{number}"]
                party.append(mon)
        return party

    def find_pokecp(name):
        with open('pokecp.json') as f:
            data = json.load(f)
            return (data[str(name).capitalize()])

    @bot.command(
        name='ping',
        description="Testing if the bot is responding, PONG",
        pass_context=True
    )
    async def ping(ctx):
        if ctx.message.author.id in bot_config['privileged_ids']:
            await bot.say(":ping_pong: Pong!")
        else:
            await bot.say('Sorry you do not have permissions to do that!')

    @bot.command(
        name='setcode',
        description="Sets the users Pokemon Go friend code",
        pass_context=True
    )
    async def setcode(ctx, friend_code):
        username = str(ctx.message.author)
        name = ctx.message.author.display_name
        userid = str(ctx.message.author.id)
        cursor2.execute("INSERT into users ("
                        "Id, Username, Friend_Code)"
                        f"VALUES(\"{userid}\", \"{username}\", "
                        f"\"{friend_code}\")"
                        "ON DUPLICATE KEY UPDATE"
                        f" Friend_Code = \"{friend_code}\";")
        database2.ping(True)
        database2.commit()
        code = f'{name}, your friend code has been set as {friend_code}'
        await bot.say(code)

    @bot.command(
        name='code',
        description='Retrieves users Pokemon Go friend code from the database',
        pass_context=True
    )
    async def code(ctx, *potential):
        if not potential:
            user = ctx.message.author
        else:
            maybe = ' '.join(potential)
            user = find_member(ctx, maybe)
        if user is None:
            await bot.say(f"Sorry but I just couldnt find a user by the name of {maybe}")
            return
        cursor2.execute(
            f"select Friend_Code from users where id = '{user.id}';")
        result = cursor2.fetchall()
        if not cursor2.rowcount:
            if ctx.message.author == user:
                await bot.say('It seems you havn\'t set your friend code yet. try setting it with `!setcode "friendcode"`')
                return
            else:
                user2 = find_memberb(ctx, maybe)
                await bot.say(f'It seems {user.display_name} hasn\'t set their friend code yet. let them know they can set it with `!setcode "friendcode"`\n Or did you possible mean {user2.display_name}\n If so you may see their code with the command `!code {user2.display_name}`')
                return
        code = result[0][0]
        if code is None:
            if ctx.message.author == user:
                await bot.say('It seems you havn\'t set your friend code yet. try setting it with `!setcode "friendcode"`')
                return
            else:
                await bot.say(f'It seems {user.display_name} hasn\'t set their friend code yet. let them know they can set it with `!setcode "friendcode"`')
                return
        title = f'{user.display_name}\'s Friend Code is:'
        description = f'```{code}```'
        icon = bot_config['discord_icon']
        ftext = 'Click for link to easy copy'
        thumbnail = bot_config['code_thumbnail']
        color = user.colour
        if bot_config['Worldopole']:
            baseurl = bot_config['W_baseurl']
            url = f'{baseurl}index.php?page=friends&user={user.display_name.replace(" ", "")}&code={code}'
        embed = discord.Embed(title=title, url=url,
                              colour=color, description=description)
        embed.set_footer(text=ftext, icon_url=icon)
        embed.set_thumbnail(url=thumbnail)
        await bot.send_message(ctx.message.channel, embed=embed)

    @bot.command(
        name='setloc',
        description="To set your location to be displayed on your trainer cart",
        pass_context=True
    )
    async def setloc(ctx, *location):
        user = ctx.message.author
        username = str(user)
        userid = str(user.id)
        location = ' '.join(location)
        cursor2.execute("INSERT into users ("
                        "Id, Username, location)"
                        f"VALUES(\"{userid}\", \"{username}\", "
                        f"\"{location}\")"
                        "ON DUPLICATE KEY UPDATE"
                        f" location = \"{location}\";")
        database2.ping(True)
        database2.commit()
        await bot.say(f'Your location has been set to: {location}')
        return


    @bot.command(
        name='setsilph',
        description="To set your location to be displayed on your trainer cart",
        pass_context=True
    )
    async def setsilph(ctx, *silphname):
        user = ctx.message.author
        username = str(user)
        userid = str(user.id)
        silphname = ' '.join(silphname)
        cursor2.execute("INSERT into users ("
                        "Id, Username, Silph_Name)"
                        f"VALUES(\"{userid}\", \"{username}\", "
                        f"\"{silphname}\")"
                        "ON DUPLICATE KEY UPDATE"
                        f" Silph_Name = \"{silphname}\";")
        database2.ping(True)
        database2.commit()
        await bot.say(f'Your Silph Username has been set to: {silphname}')
        return

    @bot.command(
        name='delibird',
        description="Don't",
        pass_context=True
    )
    async def delibird(ctx):
        await bot.say('GET OUT!!!, \nJust get out now.....')
        return

    @bot.command(
        name='silph',
        description="Under construction",
        pass_context=True
    )
    async def silph(ctx, *potential):
        if not potential:
            user = ctx.message.author
            notset = f"{user.display_name}, it seems your Silph League username is different than your Discord username. Use the command `!setsilph` to set your username"
        else:
            maybe = ' '.join(potential)
            user = find_member(ctx, maybe)
            notset = f"It seems {user.display_name} has not set their Silph League username, let them know they can with the `!setsilph` command"
        if user is None:
            await bot.say(f"Sorry but I just couldnt find a user by the name of {maybe}")
            return
        cursor2.execute(
            f"SELECT Silph_Name, Friend_Code, location FROM users WHERE Id = '{user.id}';")
        results = cursor2.fetchall()
        silphname = user.name
        silphname = silphname.replace(' ', '')
        url = f"https://sil.ph/{silphname}.json"
        r = requests.get(url)
        try:
            if r.status_code != requests.codes.ok and results[0][0] != None:
                silphname = results[0][0]
                url = f"https://sil.ph/{silphname}.json"
                r = requests.get(url)
                if r.status_code != requests.codes.ok:
                    await bot.say(notset)
                    return
        except IndexError:
            await bot.say(notset)
            return
        silph = r.json()
        data = silph['data']
        title = f'{user.display_name}\'s Silph League Trainer Card'
        if results[0][2] is None:
            location = data['home_region']
        else:
            location = results[0][2]
        eurl = url.replace('.json', '')
        description = f"**Pokémon Go Friend Code**: `{results[0][1]}`\n**Location**: {location}\n**Play Style**: {data['playstyle']}\n**Raids/Week**: {data['raid_average']}\n**Goals**: {data['goal']}"
        icon = 'https://assets.sil.ph/silph-league/assets/silph-league-logo/logo.png'
        ftext = f"Card last modified - {data['modified']}"
        thumbnail = data['avatar']
        color = user.colour
        ename1 = '__In-Game Info__'
        evalue1 = f"**Level**: {str(data['trainer_level'])}\n**Total XP** {str(data['xp'])}\n**Pokedex**: {str(data['pokedex_count'])}"
        ename2 = "__Silph Stats__"
        evalue2 = f"**Nest Reports**: {str(data['nest_migrations'])}\n**Joined**: {str(data['joined'])} \n**Handshakes**: {str(data['handshakes'])}"
        ename3 = '__Party__'
        party = data['top_6_pokemon']
        party = find_party(party)
        evalue3 = ", ".join(party)
        badges = find_badges(data['badges'])
        ename4 = '__Badges__'
        evalue4 = " ".join(badges)
        embed = discord.Embed(title=title, url=eurl,
                              colour=color, description=description)
        embed.set_footer(text=ftext, icon_url=icon)
        embed.set_thumbnail(url=thumbnail)
        embed.add_field(name=ename1, value=evalue1, inline=True)
        embed.add_field(name=ename2, value=evalue2, inline=True)
        if evalue3 != '':
            embed.add_field(name=ename3, value=evalue3, inline=False)
        if evalue4 != '':
            embed.add_field(name=ename4, value=evalue4, inline=False)
        try:
            await bot.send_message(ctx.message.channel, embed=embed)
        except:
            await bot.say('Theres seems to be an error')

    @bot.command(
        name='directions',
        description="your local gym directory... IN BOT FORM!!!",
        pass_context=True
    )
    async def directions(ctx, *gymname):
        gym_name = ' '.join(gymname)
        if bot_config['maptype'] == 'monocle':
            cursor.execute('SELECT name FROM forts;')
        elif bot_config['maptype'] == 'rocketmap':
            cursor.execute('SELECT name FROM gymdetails;')
        gymlist = cursor.fetchall()
        gyms = []
        for gym in gymlist:
            gyms.append(str(gym[0]))
        results = process.extractOne(
            gym_name, gyms, scorer=fuzz.ratio, score_cutoff=75)
        if results != None:
            if bot_config['maptype'] == 'monocle':
                cursor.execute(f"SELECT lat, lon FROM forts WHERE name like '{results[0]}';")
            elif bot_config['maptype'] == 'rocketmap':
                cursor.execute(f"SELECT a.latitude, a.longitude from gym a inner join gymdetails b on a.gym_id = b.gym_id where b.name like '{results[0]}';")
            lat_lon = cursor.fetchall()
            if cursor.rowcount:
                point = f"{lat_lon[0][0]},{lat_lon[0][1]}"
                apikey = bot_config['api_key']
                url = f'https://www.google.com/maps/?q={point}'
                image = f'https://maps.googleapis.com/maps/api/staticmap?autoscale=1&size=600x300&maptype=roadmap&key={apikey}&format=png&visual_refresh=true&markers=size:small%7Ccolor:0x9f009f%7Cshadow:true%7C{point}'
                color = ctx.message.author.colour
                title = f'Here are directions to {results[0]}'
                embed = discord.Embed(title=title, url=url, color=color)
                embed.set_image(url=image)
                try:
                    await bot.send_message(ctx.message.channel, embed=embed)
                except:
                    bot.say('Well this is highly illogical')
        else:
            gymresults = process.extract(gym_name, gyms, limit=3)
            gym = []
            for gyms in gymresults:
                gym.append(gyms[0])
            botmsg = await bot.say(f"I can't seem to find the gym you're looking for, was it by chance one of these:\n{gym}")

    bot.run(bot_config['bot_token'])


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Does a thing to some stuff.",
        epilog=""
    )
    # TODO Specify your real parameters here.
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        help="Bot Configuration File",
        metavar="bot_config"
    )
    loglevel_group = parser.add_mutually_exclusive_group(required=False)
    loglevel_group.add_argument(
        "-v",
        "--verbose",
        help="increase output verbosity",
        action="count",
        default=0)
    loglevel_group.add_argument(
        "-q",
        "--quiet",
        help="decrease output verbosity",
        action="count",
        default=0)
    args = parser.parse_args()

    # Setup logging
    # script -vv -> DEBUG
    # script -v -> INFO
    # script -> WARNING
    # script -q -> ERROR
    # script -qq -> CRITICAL
    # script -qqq -> no logging at all
    loglevel = logging.WARNING + 10*args.quiet - 10*args.verbose
    # Set 'max'/'min' levels for logging
    if loglevel > 50:
        loglevel = 50
    elif loglevel < 10:
        loglevel = 10

    main(args, loglevel)
