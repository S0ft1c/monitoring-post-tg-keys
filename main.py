from telethon.tl.functions.channels import JoinChannelRequest
import telethon
from config import *
from database import duck

# config data
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

    container_name = db.sql_req(f"""select container from channels where id='{peer_id}'""").fetchone()[0]
    print(container_name)

    # get plus and minus
    plus = (db.sql_req(f"""select plus from containers where plus is not null and 
                container = '{container_name}'""").fetchone()[0]).split(";")

    minus = (db.sql_req(f"""select minus from containers where minus is not null and 
                container = '{container_name}'""").fetchone()[0]).split(";")

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
                response = await client.forward_messages(int(chat[0]), event.message)
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
            channel_name, container = msg.split("|")

            db.sql_req(f"""insert into channels (id, channel_name, container) values (
            {await client.get_peer_id(channel_name)}, '{channel_name}', '{container}')""")

            # join to channel
            await client(JoinChannelRequest(await client.get_entity(channel_name)))

            # update chats variable
            chats = [f"@{el[0]}" for el in db.sql_req("""select channel_name from channels""").fetchall()]
            print(chats)

            # update function ( add chats )
            @client.on(telethon.events.NewMessage(chats))
            async def check_chat(event):
                await start_check_chat(event)

        elif "add_group" in str(event.message.text):  # add_group command
            msg = str(event.message.text).replace("!add_group ", "")
            container_name, plus, minus = msg.split("|")

            db.sql_req(f"""insert into containers (container, plus, minus) values (
                        '{container_name}', '{plus}', '{minus}')""")


        elif "edit" in str(event.message.text):  # edit command
            msg = str(event.message.text).replace("!edit ", "")
            container_name, plus, minus = msg.split("|")

            if plus != 'default':
                db.sql_req(f"""update containers
                set plus='{plus}'
                where container='{container_name}'""")

            if minus != 'default':
                db.sql_req(f"""update containers
                                set minus='{minus}'
                                where container='{container_name}'""")


        elif "del_channel" in str(event.message.text):  # del_channel command
            msg = str(event.message.text).replace("!del_channel ", "")
            channel_name = msg
            db.sql_req(f"""delete from channels where channel_name='{channel_name}'""")

        elif "del_group" in str(event.message.text):  # del_group command
            msg = str(event.message.text).replace("!del_group ", "")
            container = msg
            db.sql_req(f"""delete from containers where container='{container}'""")
            db.sql_req(f"""delete from channels where container='{container}'""")

        elif "list" in str(event.message.text):  # list command
            for line in db.sql_req("select * from containers").fetchall():
                container, plus, minus = line[0], line[1], line[2]
                channels = db.sql_req(f"select channel_name from channels where container='{container}'").fetchall()

                msg = f"""Группа -> {container}
                
Плюс-слова: {plus}

Минус-слова: {minus}

Подключенные к группе каналы: {", ".join([el[0] for el in channels])}"""

                await client.send_message(main_channel, message=msg)

            chats = db.sql_req("select chat_name from chats").fetchall()
            msg = f"""Каналы для вывода информации на данный момент: {", ".join([el[0] for el in chats])}"""
            await client.send_message(main_channel, message=msg)

        elif "add_out" in str(event.message.text):  # add_out command
            msg = str(event.message.text).replace("!add_out ", "")
            chat_name = msg
            db.sql_req(f"""insert into chats (id, chat_name) values (
                        '{await client.get_peer_id(chat_name)}', '{chat_name}')""")

        elif "help" in str(event.message.text):  # command help
            # TODO: write good text for command help
            await client.send_message(main_channel, message="""""")
        else:
            await client.send_message(main_channel, message='Нет такой команды')


client.run_until_disconnected()
