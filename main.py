from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.utils import get_peer_id
from dotenv import load_dotenv
from os import getenv
from bing import Bing, Tones
import json
import sqlite3
import db

with open("config.json", "r", encoding="utf-8") as f:
    data = f.read()
    config = json.loads(data)

try:
    api_id = config["api_id"]
    api_hash = config["api_hash"]
    bot_token = config["bot_token"]
except:
    raise Exception('API_ID, API_HASH and BOT_TOKEN must be set in config.json')

allowed_ids = config["allowed_ids"]

if not api_id or not api_hash or not bot_token:
    raise Exception('API_ID, API_HASH and BOT_TOKEN must be set in .env file')

default_tone = config["default_tone"]
if default_tone not in ["creative", "precise", "balanced"]:
    raise Exception("Tone is not in the allowed list.")

with open("roles.json", "r", encoding="utf-8") as f:
    available_roles = f.read()
available_roles = json.loads(available_roles)

default_role = config["default_role"]
if default_role not in available_roles:
    raise Exception("Add the role in roles.json")

con = sqlite3.connect("chats.db")

db.create_tables(con.cursor())
for id in allowed_ids:
    db.Chat.insert_chat(con, id, default_role, default_tone)

client = TelegramClient('bot', api_id, api_hash)

async def AiAgent(prompt, msg, system_prompt="", tone=Tones.creative):
    req = Bing().create_async_generator("gpt-4", [{"content": system_prompt, "role": "system"},{"content": prompt, "role": "user"}], tone=tone)
    full_text = ""
    async for message in req:
        full_text += message
        if message != "":
            try:
                await msg.edit(full_text)
            except:
                pass
    if full_text == "":
        await msg.edit("Empty response from Bing")

@client.on(NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hey! Write something and I will answer you using the gpt-4 model or add me to a group and I will answer you when you mention me.')

@client.on(NewMessage(pattern='/help'))
async def help(event):
    await event.respond('Hey! Write something and I will answer you using the gpt-4 model or add me to a group and I will answer you when you mention me.\nCommands:\n\n/role - Switches the role (current roles: dan, magician, stan, mongo, devmode, aim)\n\n/newroles - Adds a new role to the role json\n\n/roles - Displays the current roles.\n\n/gpt - Scrapes Bing AI')

@client.on(NewMessage(pattern="/tone"))
async def tone(event):
    global con
    peer_id = get_peer_id(event.message.peer_id)
    try:
        loc_tone = event.text.split(" ")[1]
    except IndexError:
        await event.respond("You need to specify a role.")
        return
    resp = ""
    if loc_tone not in ["creative", "balanced", "precise"]:
        resp = f"Tone set to ${loc_tone}"
        db.Chat.update_tone(con, peer_id, loc_tone)
    else:
        resp = "Tone isn't available"
    await event.reply(resp)

@client.on(NewMessage(pattern="/roles"))
async def roles(event):
    global available_roles
    await event.respond("Available roles:\n{}".format("\n".join(available_roles.keys())))

@client.on(NewMessage(pattern="/role"))
async def role(event):
    global con
    if event.text.startswith("/roles"):
        return
    peer_id = get_peer_id(event.message.peer_id)
    try:
        loc_role = event.text.split(" ")[1]
    except IndexError:
        await event.respond("You need to specify a role.")
        return
    if loc_role == "disable":
        db.Chat.update_role(con, peer_id, None)
        await event.respond("Role disabled")
        return
    elif loc_role in available_roles:
        db.Chat.update_role(con, peer_id, loc_role)
        await event.respond("Role set")
    else:
        await event.respond("Role not found")

@client.on(NewMessage(pattern="/gpt"))
async def gpt(event):
    global client, ROLE, TONE, allowed_ids
    peer_id = get_peer_id(event.message.peer_id)
    if peer_id not in allowed_ids:
        await event.reply("Can't respond in this chat.")
        return
    chat = db.Chat.get_chat(con.cursor(), peer_id)
    my_id = await client.get_me()
    my_id = my_id.id
    my_username = await client.get_me()
    my_username = my_username.username
    prompt = event.text.replace(f'/gpt', '')
    msg = await event.reply('Thinking...')
    system_prompt = available_roles[chat.role] if chat.role is not None else ""
    tone = chat.tone
    await AiAgent(prompt, msg, system_prompt, tone)

client.start(bot_token=bot_token)
client.run_until_disconnected()