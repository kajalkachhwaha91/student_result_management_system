from fastapi import APIRouter

router = APIRouter(
    prefix="/roles",
    tags=["Roles"]
)

# Static roles list — later can be fetched from DB
ROLES = [
    {"id": 1, "name": "Admin"},
    {"id": 2, "name": "Teacher"},
    {"id": 3, "name": "Student"}
]

@router.get("/")
def get_roles():
    """
    Get all available roles for dropdown.
    """
    return {"roles": ROLES}
