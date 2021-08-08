import os
import discord
from discord.ext import commands
import requests
import json
import binascii
from dotenv import load_dotenv
import redis

'''
A simple Discord bot which will return the current crypto greed and fear index
Commands can be invoked directly from the Discord server

Response from the API will be cached in a redis cache for 1 hour
'''

load_dotenv()
# set the environment variable to Discord server token
TOKEN = os.getenv('DISCORD_TOKEN')

emojis = [u'\U0001F631', u'\U0001F61F', u'\U0001F610', u'\U0001F60B', u'\U0001F924']
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
url = "https://api.alternative.me/fng/?limit=2"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11.2; rv:88.0) Gecko/20100101 Firefox/88.0'}

bot = commands.Bot(command_prefix="!")

# command name can be specified here
# to use it, enter the command as !index
@bot.command(name='index')
async def on_message(ctx):
    if r.get('value') == None:
        res = requests.get(url, headers=headers)
        response = res.text

        d = json.loads(response)

        value = d["data"][0]["value_classification"]
        score = d["data"][0]["value"]

        r.set('value', value)
        r.expire('value', 3600)
        r.set('score', score)
        r.expire('score', 3600)
    else:
        value = r.get('value')
        score = r.get('score')

    if value.lower() == "extreme fear":
        emoji = emojis[0]
    elif value.lower() == "fear":
        emoji = emojis[1]
    elif value.lower() == "neutral":
        emoji = emojis[2]
    elif value.lower() == "greed":
        emoji = emojis[3]
    elif value.lower() == "extreme greed":
        emoji = emojis[4]
    
    msg = "Crypto greed and fear index rating is: " + value + " right now " + emoji + "\n" + "score: " + score

    await ctx.send(msg)

bot.run(TOKEN)
