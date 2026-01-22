from fastapi import APIRouter, Depends, HTTPException, Response
from datetime import datetime, date
from bson import ObjectId

from backend.app.utils.mongo import serialize_mongo
from backend.app.db.connection import bonafide_collection, student_collection
from backend.app.schemas.bonafide_schema import (
    BonafideRequestSchema,
    BonafideApprovalSchema,
)
from backend.app.dependencies import get_current_student, get_current_teacher
from backend.app.utils.pdf import generate_bonafide_pdf

router = APIRouter(tags=["Bonafide"])


# ===============================
# STUDENT → REQUEST BONAFIDE
# ===============================
@router.post("/students/bonafide/request")
async def request_bonafide(
    payload: BonafideRequestSchema,
    current_user: dict = Depends(get_current_student),
):
    # ✅ Prevent multiple pending requests
    existing = await bonafide_collection.find_one({
        "student_id": current_user["_id"],
        "status": "PENDING"
    })

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have a pending bonafide request"
        )

    bonafide_doc = {
        "student_id": current_user["_id"],
        "reason": payload.reason,
        "status": "PENDING",
        "approved_by": None,
        "created_at": datetime.utcnow(),
        "approved_at": None,
    }

    await bonafide_collection.insert_one(bonafide_doc)

    return {"message": "Bonafide request submitted successfully"}


# ===============================
# TEACHER → VIEW PENDING REQUESTS
# ===============================
@router.get("/teachers/bonafide/pending")
async def get_pending_bonafide_requests(
    current_teacher: dict = Depends(get_current_teacher),
):
    pending = []

    cursor = bonafide_collection.find({"status": "PENDING"})
    async for req in cursor:
        pending.append(serialize_mongo(req))

    return pending


# ===============================
# TEACHER → APPROVE / REJECT
# ===============================
@router.put("/teachers/bonafide/{request_id}/approve")
async def approve_bonafide(
    request_id: str,
    payload: BonafideApprovalSchema,
    current_teacher: dict = Depends(get_current_teacher),
):
    result = await bonafide_collection.update_one(
        {"_id": ObjectId(request_id)},
        {
            "$set": {
                "status": payload.status,
                "approved_by": current_teacher["_id"],
                "approved_at": datetime.utcnow(),
            }
        }
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")

    return {"message": f"Request {payload.status.lower()} successfully"}


# ===============================
# STUDENT → DOWNLOAD PDF
# ===============================
@router.get("/students/bonafide/{request_id}/pdf")
async def download_bonafide(
    request_id: str,
    current_user: dict = Depends(get_current_student),
):
    request = await bonafide_collection.find_one({
        "_id": ObjectId(request_id),
        "student_id": current_user["_id"],
        "status": "APPROVED",
    })

    if not request:
        raise HTTPException(status_code=403, detail="Not authorized")

    student = await student_collection.find_one({
       "email": current_user["email"]
    })

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    pdf = generate_bonafide_pdf({
        "name": student["name"],
        "enrollment": student["enrollment_no"],
        "course": student["course"],
        "year": "2024-25",
        "reason": request["reason"],
        "date": date.today().strftime("%d-%m-%Y"),
    })

    return Response(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=bonafide.pdf"
        },
    )
