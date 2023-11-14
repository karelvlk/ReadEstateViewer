import psycopg2
from psycopg2 import pool

class PostgresClient:
    def __init__(self, db_config):
        self.pool = psycopg2.pool.SimpleConnectionPool(1, 10, **db_config)

    def create_table(self):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255),
                    img_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
                cursor.execute(create_table_query)
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def insert_data(self, title, img_url):
        conn = self.pool.getconn()
        try:
            with conn.cursor() as cursor:
                insert_query = "INSERT INTO images (title, img_url) VALUES (%s, %s)"
                cursor.execute(insert_query, (title, img_url))
            conn.commit()
        finally:
            self.pool.putconn(conn)

    def close_pool(self):
        self.pool.closeall()

