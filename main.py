from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def check_health():
    return {"status": "ok"}

if __name__ == "__main__":
    main()
