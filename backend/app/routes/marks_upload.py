from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import pandas as pd
from backend.app.db.connection import result_collection
import os
from fastapi.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

router = APIRouter(prefix="/marks", tags=["Marks"])

@router.post("/upload")
async def upload_marks(
    file: UploadFile = File(...),
    max_marks_per_subject: int = Query(100, description="Maximum marks per subject (default 100)")
):
    # Validate file type
    if not (file.filename.endswith(".xlsx") or file.filename.endswith(".csv")):
        raise HTTPException(status_code=400, detail="Only Excel or CSV files allowed")

    # Read file into dataframe
    if file.filename.endswith(".xlsx"):
        df = pd.read_excel(file.file)
    else:
        df = pd.read_csv(file.file)

    # Required column
    if "StudentID" not in df.columns:
        raise HTTPException(status_code=400, detail="Missing StudentID column")

    # Determine subject columns (exclude StudentID and any previously added columns)
    excluded = {"StudentID", "Total", "Percentage", "Grade"}
    subject_cols = [c for c in df.columns if c not in excluded]

    if not subject_cols:
        raise HTTPException(status_code=400, detail="No subject columns found (columns other than 'StudentID')")

    # Compute total from subject columns only
    df["Total"] = df[subject_cols].sum(axis=1)

    # Compute percentage correctly:
    total_max_marks = len(subject_cols) * max_marks_per_subject
    # Avoid division by zero
    if total_max_marks <= 0:
        raise HTTPException(status_code=400, detail="Invalid max marks or subject columns")

    df["Percentage"] = (df["Total"] / total_max_marks * 100).round(2)

    # Grade logic (adjust thresholds as needed)
    df["Grade"] = df["Percentage"].apply(
        lambda p: "A" if p >= 90 else "B" if p >= 75 else "C" if p >= 60 else "D"
    )

    # Prepare and insert records
    records = df.to_dict(orient="records")
    result_collection.insert_many(records)

    return {"message": "Marks uploaded successfully", "count": len(records)}



# ==============================
# 📌 DOWNLOAD RESULT API (download by student on there portal)

@router.get("/download/{student_id}")
def download_result(student_id: str):
    student = result_collection.find_one({"StudentID": student_id})
    if not student:
        raise HTTPException(status_code=404, detail="Result not found")

    os.makedirs("results", exist_ok=True)  # ✅ ensure folder exists

    pdf_path = f"results/{student_id}_result.pdf"
    c = canvas.Canvas(pdf_path, pagesize=A4)
    c.drawString(100, 780, f"Student Result: ")
    c.drawString(100, 750, f"Student ID: {student['StudentID']}")
    c.drawString(100, 730, f"Total Marks: {student.get('Total', 'N/A')}")
    c.drawString(100, 710, f"Percentage: {student.get('Percentage', 'N/A')}%")
    c.drawString(100, 690, f"Grade: {student.get('Grade', 'N/A')}")

    c.save()

    return FileResponse(
        pdf_path, media_type='application/pdf', filename=f"{student_id}_result.pdf"
    )



# ==============================
# 📌 RESULT ANALYTICS API (view by admin on there portal)
@router.get("/analytics")
def get_result_analytics():
    results = list(result_collection.find({}))
    
    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    # Convert ObjectIds and percentages safely
    for r in results:
        r["_id"] = str(r["_id"])  # <--- ADD THIS LINE
        try:
            r["Percentage"] = float(r.get("Percentage", 0))
        except (ValueError, TypeError):
            r["Percentage"] = 0

    percentages = [r["Percentage"] for r in results]
    total_students = len(percentages)
    avg_percentage = sum(percentages) / total_students if total_students else 0

    toppers = sorted(results, key=lambda r: r["Percentage"], reverse=True)[:3]

    return {
        "total_students": total_students,
        "average_percentage": round(avg_percentage, 2),
        "top_students": toppers,
    }

    results = list(result_collection.find({}))
    
    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    # Safely convert percentages to float
    percentages = []
    for r in results:
        try:
            percentages.append(float(r.get("Percentage", 0)))
        except (ValueError, TypeError):
            continue

    if not percentages:
        raise HTTPException(status_code=400, detail="No valid percentage data found")

    total_students = len(percentages)
    avg_percentage = sum(percentages) / total_students

    # Safely sort students (handling missing keys)
    toppers = sorted(
        results, key=lambda r: float(r.get("Percentage", 0)), reverse=True
    )[:3]

    return {
        "total_students": total_students,
        "average_percentage": round(avg_percentage, 2),
        "top_students": toppers,
    }
