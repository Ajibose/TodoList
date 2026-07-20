from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()


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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)