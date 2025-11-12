from fastapi import APIRouter, HTTPException
from datetime import datetime
from bson import ObjectId
from backend.app.db.connection import assignment_collection, assignment_collection, result_collection, submission_collection


router = APIRouter(prefix="/assignments", tags=["Assignments"])

# ============================================================
# 📘 1. CREATE ASSIGNMENT (By Teacher)
# ============================================================

@router.post("/create")
def create_assignment(data: dict):
    new_assignment = {
        "title": data["title"],
        "description": data["description"],
        "subject": data["subject"],
        "maxMarks": data["maxMarks"],
        "createdBy": data["teacherId"],
        "dueDate": data["dueDate"],
        "createdAt": datetime.utcnow()
    }

    result = assignment_collection.insert_one(new_assignment)
    new_assignment["_id"] = str(result.inserted_id)
    return {"message": "Assignment created successfully", "assignment": new_assignment}


# ============================================================
# 📘 2. GET ASSIGNMENTS FOR STUDENT
# ============================================================

@router.get("/student/{student_id}")
def get_assignments_for_student(student_id: str):
    assignments = list(assignment_collection.find({}))
    for a in assignments:
        a["_id"] = str(a["_id"])
        submission = submission_collection.find_one({"assignmentId": a["_id"], "studentId": student_id})
        a["status"] = submission["status"] if submission else "Pending"
        a["obtainedMarks"] = submission.get("obtainedMarks") if submission else None
    return assignments


# ============================================================
# 📘 3. STUDENT MARK ASSIGNMENT AS DONE (Submit)
# ============================================================

@router.post("/submit")
def submit_assignment(data: dict):
    assignment_id = data["assignmentId"]
    student_id = data["studentId"]

    # Prevent duplicate submission
    if submission_collection.find_one({"assignmentId": assignment_id, "studentId": student_id}):
        raise HTTPException(status_code=400, detail="Already submitted")

    new_submission = {
        "assignmentId": assignment_id,
        "studentId": student_id,
        "status": "Submitted",
        "obtainedMarks": 0,  # will be updated after teacher review
        "submittedAt": datetime.utcnow()
    }
    submission_collection.insert_one(new_submission)
    return {"message": "Assignment submitted successfully. Awaiting teacher review."}


# ============================================================
# 📘 4. TEACHER MARK SUBMISSION AS COMPLETE (Approve + Add Marks)
# ============================================================

@router.post("/verify")
def verify_submission(data: dict):
    assignment_id = data["assignmentId"]
    student_id = data["studentId"]
    obtained_marks = data.get("obtainedMarks", 0)

    submission = submission_collection.find_one({"assignmentId": assignment_id, "studentId": student_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    # Update submission status to Completed
    submission_collection.update_one(
        {"assignmentId": assignment_id, "studentId": student_id},
        {"$set": {"status": "Completed", "obtainedMarks": obtained_marks, "verifiedAt": datetime.utcnow()}}
    )

    # ✅ Update marks in result only when teacher marks completed
    existing_result = result_collection.find_one({"StudentID": student_id})
    if existing_result:
        new_total = existing_result.get("Total", 0) + obtained_marks
        new_percentage = (new_total / (len(existing_result) - 1) * 100)
        new_grade = (
            "A" if new_percentage >= 90 else
            "B" if new_percentage >= 75 else
            "C" if new_percentage >= 60 else
            "D"
        )
        result_collection.update_one(
            {"StudentID": student_id},
            {"$set": {"Total": new_total, "Percentage": new_percentage, "Grade": new_grade}}
        )

    return {"message": "Submission verified and marks added to result."}


# ============================================================
# 📘 5. TEACHER VIEW ASSIGNMENT STATUS
# ============================================================

@router.get("/status/{assignment_id}")
def view_assignment_status(assignment_id: str):
    assignment = assignment_collection.find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    submissions = list(submission_collection.find({"assignmentId": assignment_id}))
    total_submissions = len(submissions)
    completed = len([s for s in submissions if s["status"] == "Completed"])
    submitted = len([s for s in submissions if s["status"] == "Submitted"])

    return {
        "assignment": assignment["title"],
        "total_students": total_submissions,
        "submitted": submitted,
        "completed": completed,
        "pending": total_submissions - submitted
    }


# ============================================================
# 📘 6. ADMIN ANALYTICS
# ============================================================

@router.get("/analytics")
def assignment_analytics():
    all_assignments = list(assignment_collection.find({}))
    submissions = list(submission_collection.find({}))

    total_assignments = len(all_assignments)
    total_submissions = len(submissions)
    completed = len([s for s in submissions if s["status"] == "Completed"])

    avg_internal = (
        sum(s.get("obtainedMarks", 0) for s in submissions if s["status"] == "Completed") / completed
        if completed else 0
    )

    return {
        "total_assignments": total_assignments,
        "total_submissions": total_submissions,
        "completed_rate": round((completed / total_submissions) * 100, 2) if total_submissions else 0,
        "average_internal_marks": round(avg_internal, 2)
    }
