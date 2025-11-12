from fastapi import APIRouter, HTTPException
from backend.app.schemas.user_schema import UserCreate
from backend.app.db.connection import user_collection
from bson import ObjectId
import bcrypt  # ✅ for password hashing

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

# ==============================
# 📌 SIGNUP API
# ==============================
def email_exists(email: str):
    return user_collection.find_one({"email": email})

@router.post("/signup")
def create_user(user: UserCreate):
    # ✅ 1. Check for duplicate email
    if email_exists(user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # ✅ 2. Validate role
    valid_roles = ["Student", "Teacher", "Admin"]
    if user.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    # ✅ 3. Hash password
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())

    # ✅ 4. Prepare user object
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw.decode('utf-8'),
        "role": user.role
    }

    # ✅ 5. Insert into MongoDB
    result = user_collection.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return {"message": "User created successfully", "user": new_user}


# ==============================
# 📌 FETCH USERS BY ROLE
# ==============================

# ✅ Get all Students
@router.get("/students")
def get_students():
    students = list(user_collection.find({"role": "Student"}))
    for student in students:
        student["_id"] = str(student["_id"])
    return {"count": len(students), "students": students}


# ✅ Get all Teachers
@router.get("/teachers")
def get_teachers():
    teachers = list(user_collection.find({"role": "Teacher"}))
    for teacher in teachers:
        teacher["_id"] = str(teacher["_id"])
    return {"count": len(teachers), "teachers": teachers}


# ✅ Get all Admins
@router.get("/admins")
def get_admins():
    admins = list(user_collection.find({"role": "Admin"}))
    for admin in admins:
        admin["_id"] = str(admin["_id"])
    return {"count": len(admins), "admins": admins}
