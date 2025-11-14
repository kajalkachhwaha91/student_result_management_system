from fastapi import APIRouter, HTTPException, Header
from backend.app.db.database import get_db
from backend.app.schemas.user_schema import UserLogin
from jose import jwt, JWTError
import bcrypt, datetime, os

router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise Exception("SECRET_KEY missing!")

ALGORITHM = "HS256"

# ===============================
# LOGIN (ASYNC + MOTOR)
# ===============================
@router.post("/auth/login")
async def login(user: UserLogin):
    db = get_db()

    db_user = await db.users.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(404, "User not found")

    if not bcrypt.checkpw(user.password.encode(), db_user["password"].encode()):
        raise HTTPException(401, "Invalid password")

    token = jwt.encode({
        "email": db_user["email"],
        "role": db_user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm=ALGORITHM)

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "name": db_user["name"],
            "email": db_user["email"],
            "role": db_user["role"]
        }
    }

# ===============================
# PROFILE (ASYNC + MOTOR)
# ===============================
@router.get("/auth/profile")
async def profile(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(401, "Invalid token")

    db = get_db()
    user = await db.users.find_one({"email": payload["email"]})

    if not user:
        raise HTTPException(404, "User not found")

    user["_id"] = str(user["_id"])
    user.pop("password", None)

    return {"user": user}

    

# ==============================
# 📌 LOGOUT API
# ==============================
@router.post("/auth/logout")
async def logout_user(authorization: str = Header(None)):
    """
    When user logs out, validate token and instruct frontend to clear it.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    try:
        token = authorization.split(" ")[1]  # Extract token from "Bearer <token>"
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return {
        "message": "Logout successful. Please clear the token from client side."
    }
