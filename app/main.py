from fastapi import FastAPI
from app.database import engine
from app import models

# This actually CREATES the tables in the database
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "BOT GPT is running!"}
