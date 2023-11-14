from postgres import PostgresClient


def init_db():
    dbConfig = {
        "user": "user1",
        "host": "db",
        "database": "sreality_db",
        "password": "password1",
        "port": 5432,
    }

    pg = PostgresClient(dbConfig)
    pg.create_table()
    pg.close_pool()


if __name__ == "__main__":
    init_db()
