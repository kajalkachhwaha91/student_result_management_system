from fastapi import APIRouter, HTTPException
from backend.app.db.database import get_db
from backend.app.schemas.user_schema import UserCreate
import bcrypt

router = APIRouter(prefix="/users", tags=["Users"])

# ============================
# 📌 SIGNUP (ASYNC + MOTOR)
# ============================
@router.post("/signup")
async def create_user(user: UserCreate):
    db = get_db()

    # 1️⃣ Check if email exists
    existing = await db.users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2️⃣ Validate role
    valid_roles = ["Student", "Teacher", "Admin"]
    if user.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role selected")

    # 3️⃣ Hash password
    hashed_pw = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    # 4️⃣ Create user object
    new_user = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw,
        "role": user.role
    }

    # Insert user
    result = await db.users.insert_one(new_user)
    new_user["_id"] = str(result.inserted_id)

    return {"message": "User created successfully", "user": new_user}



# ============================
# 📌 FETCH USERS BY ROLE (ASYNC)
# ============================

@router.get("/students")
async def get_students():
    db = get_db()

    students_cursor = db.users.find({"role": "Student"})
    students = []
    async for student in students_cursor:
        student["_id"] = str(student["_id"])
        students.append(student)

    return {"count": len(students), "students": students}


@router.get("/teachers")
async def get_teachers():
    db = get_db()

    teachers_cursor = db.users.find({"role": "Teacher"})
    teachers = []
    async for teacher in teachers_cursor:
        teacher["_id"] = str(teacher["_id"])
        teachers.append(teacher)

    return {"count": len(teachers), "teachers": teachers}


@router.get("/admins")
async def get_admins():
    db = get_db()

    admins_cursor = db.users.find({"role": "Admin"})
    admins = []
    async for admin in admins_cursor:
        admin["_id"] = str(admin["_id"])
        admins.append(admin)

    return {"count": len(admins), "admins": admins}
