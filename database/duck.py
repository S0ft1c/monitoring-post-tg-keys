import duckdb


class DuckDB(object):

    def __init__(self):
        # creating database
        self.conn = duckdb.connect('database.duckdb')
        self.c = self.conn.cursor()

        # creating tables in database
        self.c.sql("""create table if not exists channels (
        id integer primary key not null,
        channel_name string,
        plus string, 
        minus string
        )""")

        self.c.sql("""create table if not exists chats (
        id integer primary key,
        chat_name string,
        )""")

    def sql_req(self, req: str):
        return self.c.sql(req)

    # def insert_channels(self, data):
    #     self.c.sql("""insert into chanells (chanells, plus, minus) values (
    #             ?, ?, ?
    #             )""", ())

    def __del__(self):
        self.conn.close()

