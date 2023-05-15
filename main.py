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


# create start function
@client.on(telethon.events.NewMessage(chats))
async def start_check_chat(event):
    print(event)

    # get peer_id
    peer_id = '-100' + str(event.original_update.message.peer_id.channel_id)
    print(peer_id)

    # get plus and minus
    plus = (db.sql_req(f"""select plus from channels where plus is not null and 
                id = '{peer_id}'""").fetchone()[0]).split(";")

    minus = (db.sql_req(f"""select minus from channels where minus is not null and 
                id = '{peer_id}'""").fetchone()[0]).split(";")

    print(plus, minus)

    # receive all chats that we need to send message
    where = (db.sql_req("""select chat_name from chats"""))
    if where is not None:
        where = where.fetchall()
    print(where)

    # check for minus words
    good = True
    for el in minus:
        if str(el) in str(event.message.text):
            good = False
            break

    # if all is good
    if good:
        # check for plus words
        good = False
        for el in plus:
            if str(el) in str(event.message.text):
                good = True
                break
        # if we find +words
        if good:
            out_peer_id = db.sql_req("""select id from chats""").fetchall()
            for chat in out_peer_id:  # send messages to all needed channels
                print(chat)
                response = await client.send_message(int(chat[0]), message='yes')
                print(response)


@client.on(telethon.events.NewMessage(main_channel))
async def main_receive(event):
    print(event)

    if event.message.text[0] == "!":
        # write our data to db
        db = duck.DuckDB()

        if "add_channel" in str(event.message.text):  # add_channel command
            # if it is add_channel
            msg = str(event.message.text).replace("!add_channel ", "")
            channel_name, plus, minus = msg.split("|")

            db.sql_req(f"""insert into channels (id, channel_name, plus, minus) values (
            {await client.get_peer_id(channel_name)}, '{channel_name}', '{plus}', '{minus}')""")

            # join to channel
            await client(JoinChannelRequest(await client.get_entity(channel_name)))

            # update chats variable
            chats = [f"@{el[0]}" for el in db.sql_req("""select channel_name from channels""").fetchall()]
            print(chats)

            # update function ( add chats )
            @client.on(telethon.events.NewMessage(chats))
            async def check_chat(event):
                await start_check_chat(event)

        elif "edit" in str(event.message.text):  # edit command
            msg = str(event.message.text).replace("!edit ", "")
            channel_name, plus, minus = msg.split("|")
            if plus != 'default':
                db.sql_req(f"""update channels
                set plus='{plus}'
                where channel_name='{channel_name}'""")

            if minus != 'default':
                db.sql_req(f"""update channels
                                set minus='{minus}'
                                where channel_name='{channel_name}'""")

        elif "del" in str(event.message.text):  # del command
            msg = str(event.message.text).replace("!del ", "")
            channel_name = msg
            db.sql_req(f"""delete from channels where channel_name='{channel_name}'""")

        elif "list" in str(event.message.text):  # list command
            await client.send_message(main_channel, message=str(db.sql_req("""select * from channels""")))

        elif "add_out" in str(event.message.text):  # add_out command
            msg = str(event.message.text).replace("!add_out ", "")
            chat_name = msg
            db.sql_req(f"""insert into chats (id, chat_name) values (
                        '{await client.get_peer_id(chat_name)}', '{chat_name}')""")

        elif "list" in str(event.message.text):  # command help
            # TODO: write good text for command help
            await client.send_message(main_channel, message="""""")
        else:
            await client.send_message(main_channel, message='Нет такой команды')


client.run_until_disconnected()
