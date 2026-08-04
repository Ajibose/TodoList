from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import TypedDict
import sqlite3


app = FastAPI()

conn = sqlite3.connect("tasks.db", check_same_thread=False, timeout=5)
conn.row_factory = sqlite3.Row

with conn:
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute(
        """CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )"""
    )

SEED_TASKS = [
    {"title": "Finish BE assigment 1", "done": False},
    {"title": "AI fluency assignment 1", "done": True},
    {"title": "Watch Kanz day 2 recording", "done": False},
]


class Task(TypedDict):
    id: int
    title: str
    done: bool


class TaskGet(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


def seed_db(cur, tasks):
    for task in tasks:
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task["title"], task["done"]),
        )


with conn:
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM tasks")
    row_count = cur.fetchone()
    if row_count[0] == 0:
        seed_db(cur, SEED_TASKS)


def db_error_response():
    return JSONResponse(status_code=500, content={"error": "database error"})


def row_to_task(row) -> Task:
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


@app.get("/")
async def root():
    """Describe the API"""
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def check_health():
    """Checks the status of the API"""
    return {"status": "ok"}


@app.get("/tasks")
def get_all_tasks(done: bool | None = None, search: str | None = None):
    """Retrived all stored tasks"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        result = cur.fetchall()
    except sqlite3.Error:
        return db_error_response()

    tasks = [row_to_task(task) for task in result]

    if done is not None:
        tasks = [task for task in tasks if task["done"] == done]

    if search:
        tasks = [task for task in tasks if search in task["title"]]

    return tasks


@app.get("/stats")
async def get_api_stats():
    """Get the API stats"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM tasks WHERE done = 1")
        done_tasks_size = cur.fetchone()[0]
    except sqlite3.Error:
        return db_error_response()

    opened_tasks = total_tasks - done_tasks_size

    return {"total": total_tasks, "done": done_tasks_size, "open": opened_tasks}


@app.get("/tasks/{id}")
async def get_task(id: int):
    """Get task with id from the stored tasks or 404 if not found"""
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        task = cur.fetchone()
    except sqlite3.Error:
        return db_error_response()

    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

    return row_to_task(task)


@app.post("/tasks", status_code=201)
async def create_task(task: TaskGet):
    """Create a new task
        Return 400 if title is absent or empty
    """
    if not task.title:
        return JSONResponse(status_code=400, content={"error": "title is empty"})

    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title, False),
        )
        conn.commit()
        new_id = cur.lastrowid
    except sqlite3.Error:
        return db_error_response()

    return {"id": new_id, "title": task.title, "done": False}


@app.put("/tasks/{id}", status_code=200)
async def update_task(id: int, data: TaskUpdate):
    """Update task with the id
    Return 404 if no task with that id found
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        task = cur.fetchone()

        if not task:
            return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

        new_title = data.title if data.title is not None else task["title"]
        new_done = data.done if data.done is not None else bool(task["done"])

        cur.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, new_done, id),
        )
        conn.commit()
    except sqlite3.Error:
        return db_error_response()

    return {"id": id, "title": new_title, "done": new_done}


@app.delete("/tasks/{id}", status_code=204)
async def remove_task(id: int):
    """Remove a task from the stored tasks

    Return 404 if no task found
    """
    try:
        cur = conn.cursor()
        cur.execute("SELECT id FROM tasks WHERE id = ?", (id,))
        task = cur.fetchone()

        if not task:
            return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

        cur.execute("DELETE FROM tasks WHERE id = ?", (id,))
        conn.commit()
    except sqlite3.Error:
        return db_error_response()


@app.post("/reset", status_code=204)
async def reset_tasks():
    """Reset the tasks to the initial tasks"""
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks")
        seed_db(cur, SEED_TASKS)
        conn.commit()
    except sqlite3.Error:
        return db_error_response()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
