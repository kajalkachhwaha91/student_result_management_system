from fastapi import Header, HTTPException
from jose import jwt, JWTError
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


async def get_current_user(authorization: str = Header(None)):
    if not authorization:
        return None

    try:
        token = authorization.split(" ")[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except (JWTError, IndexError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # 🔥 TRUST JWT ROLE (frontend-selected)
    return {
        "email": payload.get("email"),
        "role": payload.get("role"),  # ✅ THIS IS THE FIX
    }
