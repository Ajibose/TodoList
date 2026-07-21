from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    done: bool

class TaskGet(BaseModel):
    title: str | None = None

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

@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def check_health():
    return {"status": "ok"}


@app.get("/tasks")
async def get_all_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task

    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=201)
async def create_task(task: TaskGet):

    if not task.title:
        return JSONResponse(status_code=400, content={"error": "title is empty"})

    last_id = tasks[-1]["id"] if tasks else 0

    new_task = Task(
        id=last_id + 1,
        title=task.title,
        done=False
    )

    tasks.append(new_task)
    return new_task

# @app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)