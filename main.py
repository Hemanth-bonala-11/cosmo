from fastapi import FastAPI
from pymongo import MongoClient
from decouple import config
from routes.students import students_router

app = FastAPI()



@app.on_event("startup")
def connect_mongodb():
    try:
        MONGODB_URI = config("MONGODB_URI")
        app.mongo_client = MongoClient(MONGODB_URI)
        app.mongodb_database = app.mongo_client.cosmo
        app.mongodb_collection = app.mongodb_database.cosmocloud

        print("mongo db connected")
    except Exception as e:
        raise ValueError({"error": str(e)})

@app.on_event("shutdown")
def close_mongodb_connection():
    app.mongo_client.close()
    print("DB Connection Closed")


app.include_router(students_router, tags=["students"], prefix="/students")
