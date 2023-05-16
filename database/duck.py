import duckdb


class DuckDB(object):

    def __init__(self):
        # creating database
        self.conn = duckdb.connect('database.duckdb')
        self.c = self.conn.cursor()

        self.c.sql("""create table if not exists containers (
        container string,
        plus string,
        minus string,
        )""")

        # creating tables in database
        self.c.sql("""create table if not exists channels (
        id string primary key,
        channel_name string,
        container string,
        )""")

        self.c.sql("""create table if not exists chats (
        id string primary key,
        chat_name string,
        )""")

    def sql_req(self, req: str):
        return self.c.sql(req)


    def __del__(self):
        self.conn.close()

