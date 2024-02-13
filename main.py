from telethon import TelegramClient
from telethon.events import NewMessage
from telethon.utils import get_peer_id
from dotenv import load_dotenv
from os import getenv
from bing import Bing, Tones
import json
from uuid import uuid4

load_dotenv()

api_id = getenv('API_ID')
api_hash = getenv('API_HASH')
bot_token = getenv('BOT_TOKEN')

# Change this to allow chats (users and channels). Use integers for ids
allowed_ids = []

if not api_id or not api_hash or not bot_token:
    raise Exception('API_ID, API_HASH and BOT_TOKEN must be set in .env file')

client = TelegramClient('bot', api_id, api_hash)

ROLE = ""
TONE = Tones.creative

async def AiAgent(prompt, system_prompt="", tone=Tones.creative):
    req = Bing().create_async_generator("gpt-4", [{"content": system_prompt, "role": "system"},{"content": prompt, "role": "user"}], tone=tone)
    full_text = ""
    async for message in req:
        full_text += message
    return full_text

@client.on(NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Hey! Write something and I will answer you using the gpt-4 model or add me to a group and I will answer you when you mention me.')

@client.on(NewMessage(pattern='/help'))
async def help(event):
    await event.respond('Hey! Write something and I will answer you using the gpt-4 model or add me to a group and I will answer you when you mention me.\nCommands:\n\n/role - Switches the role (current roles: dan, magician, stan, mongo, devmode, aim)\n\n/newroles - Adds a new role to the role json\n\n/roles - Displays the current roles.\n\n/gpt - Scrapes Bing AI')

@client.on(NewMessage(pattern="/newrole"))
async def newrole(event):
    with open("roles.json", "r") as f:
        roles = f.read()
    roles = json.loads(roles)
    try:
        role_name = event.text.split(" ")[1]
        role = event.text.split(" ", 2)[2]
    except IndexError:
        await event.respond("You need to specify a role name and a role.")
        return
    roles[role_name] = role
    with open("roles.json", "w") as f:
        f.write(json.dumps(roles))
    await event.respond("Role added")

@client.on(NewMessage(pattern="/tone"))
async def tone(event):
    global TONE
    try:
        loc_tone = event.text.split(" ")[1]
    except IndexError:
        await event.respond("You need to specify a role.")
        return
    resp = ""
    if loc_tone == "creative":
        TONE = Tones.creative
        resp = "Tone set to creative"
    elif loc_tone == "balanced":
        TONE = Tones.balanced
        resp = "Tone set to balanaced"
    elif loc_tone == "precise":
        TONE = Tones.precise
        resp = "Tone set to precise"
    else:
        resp = "Tone isn't available"
    await event.reply(resp)

@client.on(NewMessage(pattern="/roles"))
async def roles(event):
    with open("roles.json", "r") as f:
        roles = f.read()
    roles = json.loads(roles)
    await event.respond("Available roles:\n{}".format("\n".join(roles.keys())))

@client.on(NewMessage(pattern="/role"))
async def role(event):
    global ROLE
    try:
        loc_role = event.text.split(" ")[1]
    except IndexError:
        await event.respond("You need to specify a role.")
        return
    if loc_role == "disable":
        ROLE = ""
        await event.respond("Role disabled")
        return
    with open("roles.json", "r", encoding="utf-8") as f:
        roles = f.read()
    roles = json.loads(roles)
    try:
        ROLE = roles[loc_role]
        await event.respond("Role set")
    except KeyError:
        await event.respond("Role not found")

@client.on(NewMessage(pattern="/gpt"))
async def gpt(event):
    global client, ROLE, TONE, allowed_ids
    peer_id = get_peer_id(event.message.peer_id)
    if peer_id not in allowed_ids:
        await event.reply("Can't respond in this chat.")
        return
    my_id = await client.get_me()
    my_id = my_id.id
    my_username = await client.get_me()
    my_username = my_username.username
    prompt = event.text.replace(f'/gpt', '')
    msg = await event.reply('Thinking...')
    system_prompt = ""
    if ROLE != "":
        system_prompt = ROLE
    result = await AiAgent(prompt, system_prompt, TONE)
    if result == "":
        result = "Empty reply from Bing"
    await msg.edit(result)

client.start(bot_token=bot_token)
client.run_until_disconnected()