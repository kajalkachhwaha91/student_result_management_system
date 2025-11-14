from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI:
    raise Exception("❌ MONGO_URI is missing! Add it in Render environment variables!")

client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

def get_db():
    return db
