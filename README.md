# Porybot
A First try go at at python and discord.py

#### Currently usages:
* Interactive sharing of Pokémon Go Friend Codes
* Incorporating the Silph League Trainer Cards into Discord
* Displaying minimap and providing directions to gyms as recorded by either a monocle or rocketmap structured database

## To Install:

This bot requires python3 and MYSQL.

after pulling the project, navigate to its folder and use

    python3 -m pip install -r requirements.txt


__Additionally you will need:__
- [Google Static Maps API Key](https://developers.google.com/maps/documentation/maps-static/intro)
 - [Discord Bot Token](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token)

*documentation can be found by following the links*

## Current Commands

1. code  --  returns the users pogo friend code from discord.  May be used by its self to call your own, or followed by a name to call theirs
2. setcode -- to initially set friend code
3. silph -- brings back a mockup of the silph league trainer card.  May be used by its self to call your own, or followed by a name to call theirs
4. setsilph -- used to set name on silphcard if different from discord
    `usercase "setsilph fallenflash"`
5. setloc -- to set location if you want to use something other than silph provides.    
    `usecase "setloc Virginia Beach, Va"`  (accepts any string)
6. directions -- returns directions to a gym in either a rocketmap or monocle structured database.  
    `usecase "directions find shiny deals at sprint"`

    All Names and Gyms are matched against a list, so misspellings and approximations are ok.



## Configuration:

Rename the config.yml.example file to config.yml

Some settings are common sense, heres some info for some that you may have questions about.

 - **command_prefix**
    - this is the letter/symbol/multiple letters, whatever you want that will preceed the commands for the bot.
 - **pm_help**
    - This is if you would like the !help command to be sent in private messages instead of posting to the discord channel.
 - **bot_token**
    - The Bot token you will recieve from the discord developer
- **privileged_ids**
    - the discord id numbers of members you want to have extra permissions for the bot (as of now only the ping command requires it, but more to come such as restablishing db connections, setting other peoples codes, etx)
- **mysql**
    - host: 127.0.0.1
    - port: 3306
    - database: 'monocle' 
    - user: 'john'
    - password: 'Starwars1'
        - if youve ever connected to mysql these are familiar to you, though...  database is to connect to your rocketmap or monocle style database.
    - database2:
        - Databas2 is for the bots database.   It can use the same as rocketmap or monocle or any other system as long as it is free to create and modify the 'users' table
- **Worldopole** 
    - true or false, if you have the worldopole project installed and oporating.  If so also included is a 'friends.page.php' file to include in your worldople pages directory.  This allows linking of friendcode cards to an easy webpage for copy/paste functionality
- **W_baseurl**
    - The base url of your worldopole site if it exists.  remember trailing /
 -** badgeserver BETA** 
    - True or False.  This allows custom emojis to work as fillins for the silph road badges.  You may join my custom [testing server](https://discord.gg/3gWEUVj) and request me to add your bot.  if you would like to upload the emojis yourself, the array of values can be found in 'pokemonlist.py'
 - **maptype**
    - Rocketmap or Monocle
- **Api_key**
    - The before mentioned google static maps key
- **discord_icon**
    - a decorational icon for footer of friend code messages, i personally used my server logo.
 - **code_thumbnail**
    - decorational thumbnail image for the friend code embeds



Samples
=================
![Friend Code](https://whgpogo.com/assets/github/friendcode.png "Logo Title Text 1")
![silphcard](https://whgpogo.com/assets/github/silphcard.png "FallenFlash's Silph Card")
![directions](https://whgpogo.com/assets/github/directions.png "Gym Directions")


### Credit to:
Smbambling whose coding i used as a heavy influence and teacher

### If you have any questions or comments find me on discord @FallenFlash#6963



