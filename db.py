from config import settings
from psycopg.rows import dict_row
import psycopg
import config

settings = config.settings

conn = psycopg.connect(settings.database_url, row_factory=dict_row)


def init_db() -> None:
    cursor = conn.cursor()

    with conn.transaction():
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS tasks(
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                done BOOLEAN NOT NULL DEFAULT False
            )"""
        )

        cursor.execute("SELECT COUNT(*) AS count FROM tasks")
        row_count = cursor.fetchone()
        if row_count["count"] == 0:
            seed_db(cursor)
        
def seed_db(cursor: psycopg.Cursor) -> None:
    tasks = [
        {
            "title": "Finish BE assigment 1",
            "done": False
        },
        {
            "title": "AI fluency assignment 1",
            "done": True
        },
        {
            "title": "Watch Kanz day 2 recording",
            "done": False
        }
    ]

    for task in tasks:
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s)",
            (task["title"], task["done"])
        )


def create_task(title: str, done: bool=False) -> dict:
    with conn.transaction():
        result = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, done)
        ) 

        task = result.fetchone()
        return task

def list_tasks(done: bool | None = None, search: str = "") -> list[dict]:
    where_clause = []
    values = []
    if done is not None:
        where_clause.append("done = %s")
        values.append(done)

    if search:
        where_clause.append("title LIKE %s")
        values.append(f"%{search}%")

    base_query = "SELECT * FROM tasks"

    if where_clause:
        base_query = f"{base_query} WHERE"
        
    with conn.transaction():
        result = conn.execute(
            f"{base_query} {' AND '.join(where_clause)} ORDER BY title", 
            tuple(values)
        )

        return result.fetchall()

def get_task(id: int) -> dict | None:
    with conn.transaction():
        result = conn.execute("SELECT * FROM tasks WHERE id = %s", (id, ))

        task = result.fetchone()
        if not task:
            return None

        return task

def update_task(id: int, done: bool | None = None, title: str | None = None) -> dict | None:
    with conn.transaction():
        cursor = conn.cursor()
        if title is not None and done is not None:
            cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *", (title, done, id))
        elif title is None and done is not None:
            cursor.execute("UPDATE tasks SET done = %s WHERE id = %s RETURNING *", (done, id))
        else:
            cursor.execute("UPDATE tasks SET title = %s WHERE id = %s RETURNING *", (title, id))

        updated_task = cursor.fetchone()

        if updated_task is None:
            return None

        
        return updated_task

def remove_task(id: int) -> dict | None:
    with conn.transaction():
        result = conn.execute("DELETE FROM tasks WHERE id = %s RETURNING *", (id, ))

        removed_task = result.fetchone() 
        if removed_task is None:
            return None

        return removed_task

def get_stat() -> dict:
    with conn.transaction():
        result = conn.execute(
            "SELECT COUNT(*) AS total,\
                COUNT(*) FILTER (WHERE done) AS done,\
                COUNT(*) FILTER (WHERE NOT done) AS open\
            FROM tasks"
        )
    
        stat = result.fetchone()

        total_tasks = stat["total"]
        done_tasks_size = stat["done"]
        opened_tasks = stat["open"]
        return {"total": total_tasks, "done": done_tasks_size, "open": opened_tasks}