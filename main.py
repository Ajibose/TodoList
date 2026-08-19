from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import TypedDict
from fastapi.exceptions import RequestValidationError

import db


app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "Invalid request body"})


db.init_db()


class Task(TypedDict):
    id: int
    title: str
    done: bool


class TaskGet(BaseModel):
    title: str | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


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

    tasks = db.list_tasks(done, search)

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

    task = db.get_task(id)

    if not task:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

    return task
    

@app.post("/tasks", status_code=201)
def create_task(task: TaskGet):
    """Create a new task
        Return 400 if title is absent or empty
    """
    if not task.title:
        return JSONResponse(status_code=400, content={"error": "title is empty"})


    task = db.create_task(task.title)

    return task

@app.put("/tasks/{id}", status_code=200)
def update_task(id: int, data: TaskUpdate):
    """Update task with the id
    Return 404 if no task with that id found
    """
    if data.title is None and data.done is None:
        return JSONResponse(status_code=400, content={"error": "Update field can't be empty"})

    if data.title == "":
        return JSONResponse(status_code=400, content={"error": "Title can't be empty"})

    task = db.update_task(id, done=data.done, title=data.title)

    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    return task

@app.delete("/tasks/{id}", status_code=204)
def remove_task(id: int):
    """Remove a task from the stored tasks

    Return 404 if no task found
    """

    task = db.remove_task(id)

    if task is None:
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

    uvicorn.run(app, host="0.0.0.0", port=3000)