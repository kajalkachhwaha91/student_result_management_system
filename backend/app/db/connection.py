from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

# ✅ Load .env variables
load_dotenv()

# ✅ Fetch environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise Exception("MONGO_URI or DATABASE_NAME missing in .env")

# ✅ Create ASYNC MongoDB client (Motor)
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# ✅ Collections (ASYNC)
user_collection = db["users"]
student_collection = db["students"]
result_collection = db["results"]
assignment_collection = db["assignments"]
submission_collection = db["submissions"]
bonafide_collection = db["bonafide_requests"]

# ❌ DO NOT use list_collection_names() with Motor at import time
