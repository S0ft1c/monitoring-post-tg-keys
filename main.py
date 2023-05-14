from asyncio import run
from telethon.tl.functions.channels import JoinChannelRequest
import telethon
from config import *
from database import duck

# cionfig data
api_id = id
api_hash = hash

# starting telethon
client = telethon.TelegramClient('sergay', api_id, api_hash, system_version="4.16.30-vxCUSTOM")
client.start()

# creating db connect
db = duck.DuckDB()
chats = [el[0] for el in db.sql_req("""select channel_name from channels""").fetchall()]


async def get_ent(name):
    return await client.get_entity(name)


@client.on(telethon.events.NewMessage(main_channel))
async def main_receive(event):
    print(event)

    if event.message.text[0] == "!":
        if "add_channel" in str(event.message.text):
            # if it is add_channel
            msg = str(event.message.text).replace("!add_channel ", "")
            channel_name, plus, minus = msg.split("|")

            # write our data to db
            db = duck.DuckDB()
            # creating good index
            if db.sql_req("""select max(id) from channels""").fetchone()[0] is not None:
                idx = db.sql_req("""select max(id) from channels""").fetchone()[0] + 1
            else:
                idx = 1

            db.sql_req(f"""insert into channels (id, channel_name, plus, minus) values (
            {idx}, '{channel_name}', '{plus}', '{minus}')""")

            # join to channel
            # updates = client(JoinChannelRequest(channel_name))

            # update chats variable
            chats = [f"@{el[0]}" for el in db.sql_req("""select channel_name from channels""").fetchall()]
            print(chats)

            # update function ( add chats )
            @client.on(telethon.events.NewMessage(chats))
            async def check_chat(event):
                print(event)
        else:
            pass


client.run_until_disconnected()
