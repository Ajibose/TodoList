from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def hello():
    return {"message": "Hello World"}


if __name__ == "__main__":
    main()
