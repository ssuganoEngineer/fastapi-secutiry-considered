from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "FastAPI"}

if __name__ == "__main__":
    uvicorn.run(app=app, port=50001)