from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import TypedDict
import sqlite3


app = FastAPI()

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
    cursor.execute("SELECT * FROM tasks")
    result = cursor.fetchall()
    tasks = [
        {"id": task["id"], "title": task["title"], "done": bool(task["done"])}
        for task in result   
    ]

    if done is not None:
        tasks = [task for task in tasks if task["done"] == done]

    if search:
        tasks = [task for task in tasks if search in task["title"]]

    return tasks

@app.get("/stats")
async def get_api_stats():
    """Get the API stats"""
    total_tasks = len(tasks)
    done_tasks_size = len(list(filter(lambda t: t["done"] == True, tasks)))
    opened_tasks = total_tasks - done_tasks_size

    return {"total": total_tasks, "done": done_tasks_size, "open": opened_tasks}

@app.get("/tasks/{id}")
async def get_task(id: int):
    """Get task with id from the stored tasks or 404 if not found"""
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (id, ))

    task = cursor.fetchone()
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    
    task = dict(task)
    task["done"] = bool(task["done"])

    return task
    

@app.post("/tasks", status_code=201)
async def create_task(task: TaskGet):
    """Create a new task
        Return 400 if title is absent or empty
    """
    if not task.title:
        return JSONResponse(status_code=400, content={"error": "title is empty"})

    last_id = tasks[-1]["id"] if tasks else 0

    new_task = {
        "id": last_id + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)
    return new_task

@app.put("/tasks/{id}", status_code=200)
async def update_task(id: int, data: TaskUpdate):
    """Update task with the id
    Return 404 if no task with that id found
    """
    task = next((task for task in tasks if task["id"] == id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    if data.title is not None:
        task["title"] = data.title

    if data.done is not None:
        task["done"] = data.done

    return task
    
@app.delete("/tasks/{id}", status_code=204)
async def remove_task(id: int):
    """Remove a task from the stored tasks

    Return 404 if no task found
    """
    task = next((task for task in tasks if task["id"] == id), None)
    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    tasks.remove(task)

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