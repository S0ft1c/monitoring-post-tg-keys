import telethon
from database import duck
from asyncio import run


async def get_ent(client, name):
    return await client.get_entity(name)


def add_channel(client):
    db = duck.DuckDB()
    channel_name, plus, minus = db.sql_req("""SELECT * FROM channels ORDER BY ID DESC LIMIT 1""")
    id_ch = get_ent(client, channel_name)

    @client.on(telethon.events.NewMessage(id_ch))
    async def check_channel(event):
        print(event.message.text)
        pass


def start_main(client, id):
    @client.on(telethon.events.NewMessage(id))
    async def main_receive(event):

        print(event.message.text)

        if event.message.text[0] == "!":
            if "add_channel" in str(event.message.text):
                msg = str(event.message.text).replace("!add_channel", "")
                channel_name, plus, minus = msg.split("|")

                db = duck.DuckDB()
                db.sql_req(f"""insert into chanells (chanell_name, plus, minus) values (
                {channel_name}, {plus}, {minus},
                )""")

                run(add_channel(client))
