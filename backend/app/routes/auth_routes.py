from fastapi import APIRouter, HTTPException, Header
from backend.app.db.connection import user_collection
from backend.app.schemas.user_schema import UserLogin
import bcrypt, jwt, datetime 
from fastapi.security import HTTPBearer
from jose import JWTError, jwt 

router = APIRouter()


security = HTTPBearer()

# ✅ Secret Key (same as used in login)
SECRET_KEY = "YOUR_SECRET_KEY"
ALGORITHM = "HS256"


# ==============================
# 📌 LOGIN API
# ==============================

@router.post("/auth/login")
async def login_user(user: UserLogin):
    db_user = user_collection.find_one({"email": user.email})

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not bcrypt.checkpw(user.password.encode('utf-8'), db_user["password"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid password")

    # ✅ Generate JWT token
    payload = {
        "email": db_user["email"],
        "role": db_user["role"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "name": db_user["name"],
            "email": db_user["email"],
            "role": db_user["role"]
        }
    }

# ==============================
# 📌 GET PROFILE API
# ==============================
@router.get("/auth/profile")
async def get_profile(authorization: str = Header(None)):
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header missing")

        token = authorization.split(" ")[1]  # "Bearer <token>"
        payload = jwt.decode(token, "YOUR_SECRET_KEY", algorithms=["HS256"])

        user = user_collection.find_one({"email": payload["email"]})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user["_id"] = str(user["_id"])
        user.pop("password", None)  # remove password before returning

        return {"user": user}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


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
