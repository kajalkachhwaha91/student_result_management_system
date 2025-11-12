from fastapi import APIRouter,  HTTPException
from backend.app.db.connection import student_collection
from backend.app.schemas.student_schema import StudentBase, StudentCreate as Student
from bson import ObjectId

router = APIRouter(prefix="/students", tags=["Students"])



@router.get("/")
def get_students():
    return {"message": "Students API is working!"}

# Sample POST route
@router.post("/")
def add_student(student: dict):
    return {"message": "Student added successfully", "data": student}