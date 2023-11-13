import psycopg2
import uvicorn
from fastapi import FastAPI, HTTPException

dbConfig = {
    "user": "user1",
    "host": "db",
    "database": "sreality_db",
    "password": "password1",
    "port": 5432,
};

DATABASE_URL = f"postgresql://{dbConfig['user']}:{dbConfig['password']}@{dbConfig['host']}/{dbConfig['database']}"
ITEMS_PER_PAGE = 20

app = FastAPI()

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

@app.get("/items-count")
async def read_item_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM images")
        count = cursor.fetchone()[0]
        return {"total_items": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()


@app.get("/items/{page}")
async def read_items(page: int):
    if page < 1:
        raise HTTPException(status_code=400, detail="Page number must be greater than 0")

    offset = (page - 1) * ITEMS_PER_PAGE

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, title, img_url, created_at FROM images LIMIT %s OFFSET %s", (ITEMS_PER_PAGE, offset))
        result = cursor.fetchall()
        return [{"id": row[0], "title": row[1], "img_url": row[2], "created_at": row[3]} for row in result]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    config = uvicorn.Config(
        "server:app",
        host="0.0.0.0",
        port=3000,
    )
    server = uvicorn.Server(config)
    server.run()
