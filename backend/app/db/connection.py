from pymongo import MongoClient
from dotenv import load_dotenv
import os

# ✅ Load .env variables
load_dotenv()

# ✅ Fetch environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# ✅ Create MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]

# ✅ Example collection
user_collection = db["users"]
student_collection = db["students"]
result_collection = db["results"]
assignment_collection = db["assignments"]
submission_collection= db["submissions"]

if __name__ == "__main__":
    print("Connected to DB:", db.name)
    print("Collections:", db.list_collection_names())
