from bs4 import BeautifulSoup
from discord.colour import Color
from discord.ext import commands, tasks
from dotenv import load_dotenv

import asyncio
import datetime
import discord
import os
import random
import re
import requests
import time
import urllib.parse

from map import load_data
from map import search

## ENV
userCooldowns = {}
agentAbilities = {'sova': ["recon", "shock"]}
author_icon = "https://emoji.gg/assets/emoji/2366_Sage_Love.png"
footer_icon = "https://emoji.gg/assets/emoji/9309_valorant_logo.png"

## Discord bot
bot = commands.Bot(command_prefix='!', help_command=None, description='This is a Valorant Tracker Bot. Data is based on Tracker.gg and Blitz.gg.\nPrefix command is "!"')

async def update_status():
    activity_string = '{} servers | !help'.format(len(bot.guilds))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=activity_string))

@bot.event
async def on_ready():
    bot.loop.create_task(update_status())

@bot.event
async def on_guild_join(guild):
    bot.loop.create_task(update_status())

@bot.event
async def on_guild_remove(guild):
    bot.loop.create_task(update_status())
    
@bot.command(name='help')
async def help(ctx, *args):
    
    if is_spam(ctx.message.author.id):
        return

    if len(args) == 0:
        # Embedded data
        embed = discord.Embed(title="List of Commands", color=0x1af0ff)
        embed.set_author(name="Valorant Buddy", icon_url=author_icon)
        embed.set_footer(text="Each command has 5 seconds cooldown | More features to come soon :)", icon_url=footer_icon)
        
        stats = "**!stats *name*#*tag*** - Get player's stats. ex, `!stats example#1234`"
        agent = "**!*agent* *ability* *map*** - Get .gif command lists for *Agent*'s *ability* all positions."
        agent_2 = "**!*agent* *ability* *map* start:*pos*** - Get .gif command lists for *Agent*'s *ability* which starts from given positions."
        agent_3 = "**!*agent* *ability* *map* dest:*pos*** - Get .gif command lists for *Agent*'s *ability* which ends on given positions."
        note = "Note: ***pos*** name will be the same as in game minimap | Attacker spawn = **tspawn** | Defender spawn = **ctspawn**"
        embed.add_field(name="Features :sparkles:", value="\n".join([stats, agent, agent_2, agent_3, note]), inline=False)

        agent_help = "**!help *agent***- Get help for *agent_name* commands. ex, `!help sova`"
        sova = "**!sova *(recon | shock)* *map*** - Get .gif command lists for Sova's (recon | shock) bolt positions. ex, `!sova recon bind`"
        agent_command_list = [agent_help, sova]
        embed.add_field(name="Supported Agents :sun_with_face:", value='\n'.join(agent_command_list), inline=False)

        register = "[**Register**](https://thetrackernetwork.com/auth/register?domain=account.tracker.gg) to Tracker.gg (official Riot API)"
        invite = "[**Invite**](https://discord.com/oauth2/authorize?client_id=" + DISCORD_APPLICATION_ID + "&permissions=456768&scope=bot) Valorant Buddy to your server"
        support = "[**Support**](https://www.paypal.com/paypalme/earthpatipon) to keep the discord bot alive :balloon:"
        embed.add_field(name="Help and Support :heartbeat:", value="\n".join([register, invite, support]), inline=False)
        await ctx.send(embed=embed)
    elif len(args) == 1:
        if args[0] not in agentAbilities:
            pass #TODO: any non agent commands
        print("[!help] sova")
        if args[0] == "sova":
            # Embedded data
            embed = discord.Embed(title="List of " + args[0].capitalize() + " Commands", color=0x1af0ff)
            embed.set_author(name="Valorant Buddy", icon_url=author_icon)
            embed.set_footer(text="Each command has 5 seconds cooldown | More features to come soon :)", icon_url=footer_icon)
            
            abilities = "**recon** *for recon bolt*     **shock** *for shock bolt*"
            embed.add_field(name="Sova's supported abilities :rainbow:", value="\n".join([abilities]), inline=False)

            maps = "**bind**"
            embed.add_field(name="Sova's supported maps :map:", value="\n".join([maps]), inline=False)

            ex_1 = "**!sova recon bind** - Get .gif command lists for Sova's recon bolt on Bind in all positions."
            ex_2 = "**!sova recon bind start:asite** - Get .gif command lists for Sova's recon bolt that starts on Bind A site, landing on any position."
            ex_3 = "**!sova shock bind dest:adefault** - Get .gif command lists for Sova's shock bolt that starts from any position, landing on A default."
            ex_4 = "**!sova recon bind start:tspawn dest:asite** - Get .gif message for Sova's recon bolt that starts from T spawn landing on A site."
            embed.add_field(name="Examples :loudspeaker:", value='\n'.join([ex_1, ex_2, ex_3, ex_4]), inline=False)

            await ctx.send(embed=embed)


@bot.command(name='stats')
async def stats(ctx, *, text):

    if is_spam(ctx.message.author.id):
        return

    if "#" not in text:
        await ctx.send("```Your input is incorrect. !help for manual```")
        return
    
    stripped = text.split("#")[0].strip() + "#" + text.split("#")[1]
    nametag = urllib.parse.quote(stripped)
    session = requests.Session()
    response = session.get("https://tracker.gg/valorant/profile/riot/" + nametag + "/overview?playlist=competitive")

    if response.status_code != 200:
        print("[!stats][FAILED] " + text)
        await ctx.send("```Player not found. This is because the player profile isn't tracked from Riot```")
        await ctx.send("```If this is your account, you can register to Tracker.gg (official Riot API) to make your stats public. | !help for manual```")
        return
    print("[!stats][SUCCESS] " + text)

    soup = BeautifulSoup(response.text, 'html.parser')
    highlight_stats = soup.find_all("div", class_='highlighted__content')
    highlight_stats = list(filter(None, remove_tag(str(highlight_stats)).split(" ")))
    giant_stats = soup.find_all("div", class_='giant-stats')
    giant_stats = list(filter(None, remove_tag(str(giant_stats)).split(" ")))
    main_stats = soup.find_all("div", class_='main')
    main_stats = list(filter(None, remove_tag(str(main_stats)).split(" ")))
    rank = highlight_stats[1].upper()

    # Embedded data
    embed = discord.Embed(title="RANK", description=rank, color=0xff5c8d)
    embed.set_author(name=text, icon_url=author_icon)
    embed.set_thumbnail(url=get_rank_img(rank))
    
    embed.set_footer(text="Please wait 5 seconds to use a command again.", icon_url=footer_icon)

    embed.add_field(name="Total Match", value= str(int(highlight_stats[-5]) + int(highlight_stats[-2])), inline=True)
    embed.add_field(name="Win %", value=highlight_stats[-3], inline=True)
    embed.add_field(name="K/D Ratio", value=giant_stats[4], inline=True)

    embed.add_field(name="Kills/Round", value=main_stats[13], inline=True)
    embed.add_field(name="Damage/Round", value=giant_stats[1], inline=True)
    embed.add_field(name="Score/Round", value=main_stats[11], inline=True)

    embed.add_field(name="Headshots %", value=giant_stats[7], inline=True)
    embed.add_field(name="Clutch", value=main_stats[20], inline=True)
    embed.add_field(name="Ace", value=main_stats[18], inline=True)
    
    embed.add_field(name="First Bloods", value=main_stats[16], inline=True)
    embed.add_field(name="Flawless", value=main_stats[22], inline=True)
    embed.add_field(name="Most Kills (Match)", value=main_stats[26], inline=True)
    await ctx.send(embed=embed)

@bot.command(name='sova')
async def agent_sova(ctx, * ,text):

    if is_spam(ctx.message.author.id):
        return
    
    validated_result = validate_agent_command(text)
    if not validated_result:
        await ctx.send("```Your input is incorrect. !help for manual```")
        return
    
    if validated_result[0] == False:
        await ctx.send("```No matching data found.\n!help sova for manual```")
        return

    embed_list = embed_agent_command("sova", validated_result)
    if isinstance(embed_list, str):
        await ctx.send(embed_list)
        return
    for embed in embed_list:
        embed.set_footer(text="Special thanks to Blitz.gg for data :)", icon_url="https://i.ibb.co/4JPyZkz/blitz-gg.png")
        await ctx.send(embed=embed)
    print("[!sova] " + text)


## Helper Functions
def is_spam(user_id):
    now = int(time.time())
    if user_id not in userCooldowns:
        userCooldowns[user_id] = now
        return False
    if now <= userCooldowns[user_id] + 5:
        return True
    else:
        userCooldowns.pop(user_id, None)
        return False

def validate_agent_command(command):
    result = []
    splits = command.lower().split(" ")
    if len(splits) == 4:                # ability map start:place dest:place
        if "start" not in splits[2] or "dest" not in splits[3]:
            pass
        result = search("sova", splits[0], splits[1], splits[2].split(":")[1], splits[3].split(":")[1])
    elif len(splits) == 3:
        if "start" in splits[2]:        # ability map start:place
            result = search("sova", splits[0], splits[1], splits[2].split(":")[1], None)
        elif "dest" in splits[2]:       # ability map dest:place
            result = search("sova", splits[0], splits[1], None, splits[2].split(":")[1])
    elif len(splits) == 2:              # ability map
        result = search("sova", splits[0], splits[1], None, None)
    else:
        pass
    return result

def embed_agent_command(agent, map_list):
    embed_list = []
    if len(map_list) == 0:
        return "```No matching data found.\nTry !sova <ability> <map> to see a list of available data```"
    elif len(map_list) == 1:
        ability = map_list[0].get_ability()
        title = prettier_map_title(map_list[0].get_start(), map_list[0].get_dest())
        embed = discord.Embed(title=title, color=0x4ae887)
        embed.set_author(name=ability.capitalize() + " Bolt", icon_url=get_agent_ability_img(agent, ability))
        embed.set_image(url=map_list[0].get_gif())
        embed_list.append(embed)
    else:
        ability = map_list[0].get_ability()
        found = []
        limit = 0
        embed = discord.Embed(title="List of available " + ability.capitalize() + " Bolt", color=random.randint(0, 0xffffff))
        for m in map_list:
            cmd = "**" + prettier_map_title(m.get_start(), m.get_dest()) + "**\n" 
            cmd += "`!sova " + ability+ " " + m.get_map_name() + " start:" + m.get_start() + " dest:" + m.get_dest() + "`\n"
            limit += len(cmd)
            if limit > 1024:
                embed.add_field(name="Copy command and paste it in channel again", value="\n".join(found), inline=False)
                embed_list.append(embed)
                embed = discord.Embed(title="List of available " + ability.capitalize() + " Bolt (Cont.)", color=random.randint(0, 0xffffff))
                found = []
                limit = 0 
            found.append(cmd)
        embed.add_field(name="Copy command and paste it in channel again", value="\n".join(found), inline=False)
        embed_list.append(embed)
    return embed_list

def prettier_map_title(start, dest):
    start_site = start[:1].capitalize() if "ct" not in start else start[:2].upper()
    start_pos = start[1:].capitalize()  if "ct" not in start else start[2:].capitalize()
    dest_site = dest[:1].capitalize() if "ct" not in dest else dest[2:].upper()
    dest_pos = dest[1:].capitalize() if "ct" not in dest else dest[:2].capitalize()
    return start_site + " " + start_pos + " To " + dest_site + " " + dest_pos

def get_agent_ability_img(agent, ability):
    if agent == "sova":
        if ability == "recon":
            return "https://i.ibb.co/Y0CfHwF/sova-recon-bolt.png"
        elif ability == "shock":
            return "https://i.ibb.co/6XSywjr/sova-shock-bolt.png"
    return False

def remove_tag(raw_html):
    cleaner = re.compile('<.*?>')
    cleantext = re.sub(cleaner, '', raw_html)
    return cleantext[1:-1].strip()

def get_rank_img(rank):
    host = "https://emoji.gg/assets/emoji/"
    if rank == "RADIANT":
        return host + "9768_Radiant_Valorant.png"
    elif rank == "IMMORTAL":
        return host + "8262_Immortal_Valorant.png"
    elif rank == "DIAMOND":
        return host + "8091_Diamond_Valorant.png"
    elif rank == "PLATINUM":
        return host + "1093_Platinium_Valorant.png"
    elif rank == "GOLD":
        return host + "6940_Gold_Valorant.png"
    elif rank == "SILVER":
        return host + "4568_Silver_Valorant.png"
    elif rank == "BRONZE":
        return host + "3375_Bronze_Valorant.png"
    else:
        return host + "7343_Fer_Valorant.png"


if __name__ == "__main__":
    load_data()
    load_dotenv()
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    DISCORD_APPLICATION_ID = os.getenv('DISCORD_APPLICATION_ID')
    bot.run(DISCORD_TOKEN)
