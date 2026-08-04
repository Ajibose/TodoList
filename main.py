from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import TypedDict
from fastapi.exceptions import RequestValidationError
import sqlite3


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


conn = sqlite3.connect("tasks.db", check_same_thread=False, timeout=5)
conn.row_factory = sqlite3.Row

cursor = conn.cursor()
cursor.execute("PRAGMA journal_mode=WAL")

cursor.execute(
    """CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        done INTEGER NOT NULL DEFAULT 0
    )"""
)
conn.commit()

class Task(TypedDict):
    id: int
    title: str
    done: bool

class TaskGet(BaseModel):
    title: str | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

tasks: list[Task] = [
    {
        "id": 1,
        "title": "Finish BE assigment 1",
        "done": False
    },
    {
        "id": 2,
        "title": "AI fluency assignment 1",
        "done": True
    },
    {
        "id": 3,
        "title": "Watch Kanz day 2 recording",
        "done": False
    }
]

def seed_db(tasks):
    for task in tasks:
        cursor.execute(
            "INSERT INTO tasks (title, done) vALUES (?, ?)",
            (task["title"], task["done"])
        )

cursor.execute("SELECT COUNT(*) FROM tasks")
row_count = cursor.fetchone()
if row_count[0] == 0:
    seed_db(tasks)
    conn.commit()


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
    where_clause = []
    values = []
    if done is not None:
        where_clause.append("done = ?")
        values.append(done)

    if search:
        where_clause.append("title LIKE ?")
        values.append(f"%{search}%")

    base_query = "SELECT * FROM tasks"

    if where_clause:
        base_query = f"{base_query} WHERE"
        

    cursor.execute(f"{base_query} {' AND '.join(where_clause)} ORDER BY title", tuple(values))
    result = cursor.fetchall()

    tasks = [
        {"id": task["id"], "title": task["title"], "done": bool(task["done"])}
        for task in result   
    ]

    return tasks

@app.get("/stats")
def get_api_stats():
    """Get the API stats"""
    cursor.execute(
        "SELECT COUNT(*) AS total,\
                SUM(done = 1) AS done,\
                SUM(done = 0) AS open\
        FROM tasks"
    )
    
    result = cursor.fetchone()

    total_tasks = result["total"]
    done_tasks_size = result["done"]
    opened_tasks = result["open"]
    return {"total": total_tasks, "done": done_tasks_size, "open": opened_tasks}

@app.get("/tasks/{id}")
def get_task(id: int):
    """Get task with id from the stored tasks or 404 if not found"""
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id, ))

    task = cursor.fetchone()
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
    task = dict(task)
    task["done"] = bool(task["done"])

    return task
    

@app.post("/tasks", status_code=201)
def create_task(task: TaskGet):
    """Create a new task
        Return 400 if title is absent or empty
    """
    if not task.title:
        return JSONResponse(status_code=400, content={"error": "title is empty"})

    cursor.execute("INSERT INTO tasks (title) VALUES (?)", (task.title, ))
    conn.commit()

    insertedID = cursor.lastrowid

    return {"id": insertedID, "title": task.title, "done": False}

@app.put("/tasks/{id}", status_code=200)
def update_task(id: int, data: TaskUpdate):
    """Update task with the id
    Return 404 if no task with that id found
    """
    if data.title is None and data.done is None:
        return JSONResponse(status_code=400, content={"error": "Update field can't be empty"})

    if data.title == "":
        return JSONResponse(status_code=400, content={"error": "Title can't be empty"})

    if data.title is not None and data.done is not None:
        cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (data.title, data.done, id))
    elif data.title is None and data.done is not None:
        cursor.execute("UPDATE tasks SET done = ? WHERE id = ?", (data.done, id))
    else:
        cursor.execute("UPDATE tasks SET title = ? WHERE id = ?", (data.title, id))

    conn.commit()

    if cursor.rowcount == 0:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id, ))
    task = dict(cursor.fetchone())

    task["done"] = bool(task["done"])

    return task

@app.delete("/tasks/{id}", status_code=204)
def remove_task(id: int):
    """Remove a task from the stored tasks

    Return 404 if no task found
    """

    cursor.execute("DELETE FROM tasks WHERE id = ?", (id, ))
    conn.commit()

    if cursor.rowcount == 0:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

@app.post("/reset", status_code=204)
async def reset_tasks():
    """Reset the tasks to the initial tasks"""
    global tasks
    tasks = [
        {
            "id": 1,
            "title": "Finish BE assigment 1",
            "done": False
        },
        {
            "id": 2,
            "title": "AI fluency assignment 1",
            "done": True
        },
        {
            "id": 3,
            "title": "Watch Kanz day 2 recording",
            "done": False
        }
    ]

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)