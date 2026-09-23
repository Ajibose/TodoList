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
                user_id UUID NOT NULL,
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
            "user_id": "b0824b2e-26aa-465f-8db3-8f79c95e1dac",
            "title": "Finish BE assigment 1",
            "done": False
        },
        {
            "user_id": "b0824b2e-26aa-465f-8db3-8f79c95e1dac",
            "title": "AI fluency assignment 1",
            "done": True
        },
        {
            "user_id": "b0824b2e-26aa-465f-8db3-8f79c95e1dac",
            "title": "Watch Kanz day 2 recording",
            "done": False
        }
    ]

    for task in tasks:
        cursor.execute(
            "INSERT INTO tasks (user_id, title, done) VALUES (%s, %s, %s)",
            (task["user_id"], task["title"], task["done"])
        )


def create_task(id, title: str, done: bool=False) -> dict:
    with conn.transaction():
        result = conn.execute(
            "INSERT INTO tasks (user_id, title, done) VALUES (%s, %s, %s) RETURNING *",
            (id, title, done)
        ) 

        task = result.fetchone()
        return task

def list_tasks(id, done: bool | None = None, search: str = "") -> list[dict]:
    where_clause = ["user_id = %s"]
    values = [id]
    if done is not None:
        where_clause.append("done = %s")
        values.append(done)

    if search:
        where_clause.append("title LIKE %s")
        values.append(f"%{search}%")

    base_query = f"SELECT * FROM tasks WHERE"
        
    with conn.transaction():
        result = conn.execute(
            f"{base_query} {' AND '.join(where_clause)} ORDER BY title", 
            tuple(values)
        )

        return result.fetchall()

def get_task(user_id: str, id: int) -> dict | None:
    with conn.transaction():
        result = conn.execute("SELECT * FROM tasks WHERE id = %s and user_id=%s", (id, user_id))

        task = result.fetchone()
        if not task:
            return None

        return task

def update_task(user_id: str, id: int, done: bool | None = None, title: str | None = None) -> dict | None:
    with conn.transaction():
        cursor = conn.cursor()
        if title is not None and done is not None:
            cursor.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s  and user_id = %s RETURNING *", (title, done, id, user_id))
        elif title is None and done is not None:
            cursor.execute("UPDATE tasks SET done = %s WHERE id = %s and user_id = %s RETURNING *", (done, id, user_id))
        else:
            cursor.execute("UPDATE tasks SET title = %s WHERE id = %s  and user_id = %s RETURNING *", (title, id, user_id))

        updated_task = cursor.fetchone()

        if updated_task is None:
            return None

        
        return updated_task

def remove_task(user_id: str, id: int) -> dict | None:
    with conn.transaction():
        result = conn.execute("DELETE FROM tasks WHERE id = %s and user_id = %s RETURNING *", (id, user_id))

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

def check_health():
    with conn.transaction():
        try:
            conn.execute("SELECT 1")
            return True
        except psycopg.Error:
            return False
    