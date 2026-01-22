from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Depends
import pandas as pd
import os
from starlette.responses import FileResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from backend.app.db.connection import result_collection, user_collection
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch




router = APIRouter(prefix="/marks", tags=["Marks"])


@router.post("/upload")
async def upload_marks(
    file: UploadFile = File(...),
    max_marks_per_subject: int = Query(100)
):
    # ✅ Validate file
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Only Excel or CSV files allowed")

    # ✅ Read file
    df = (
        pd.read_excel(file.file)
        if file.filename.endswith(".xlsx")
        else pd.read_csv(file.file)
    )

    # ✅ Normalize columns
    df.columns = df.columns.str.strip().str.lower()

    if "email" not in df.columns:
        raise HTTPException(status_code=400, detail="Missing Email column")

    excluded = {"email", "student_email", "total", "percentage", "grade"}
    subject_cols = [c for c in df.columns if c not in excluded]

    if not subject_cols:
        raise HTTPException(status_code=400, detail="No subject columns found")

    valid_records = []

    for _, row in df.iterrows():
        email = row["email"]

        # ✅ EMAIL-based validation (users collection only)
        user = await user_collection.find_one({
            "email": email,
            "role": "Student"
        })

        if not user:
            continue

        record = {sub: row[sub] for sub in subject_cols}
        record["student_email"] = email
        valid_records.append(record)

    if not valid_records:
        raise HTTPException(status_code=400, detail="No valid students found")

    df = pd.DataFrame(valid_records)

    # ✅ Marks calculation
    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["total"] = df[subject_cols].sum(axis=1)
    total_max = len(subject_cols) * max_marks_per_subject
    df["percentage"] = (df["total"] / total_max * 100).round(2)

    df["grade"] = df["percentage"].apply(
        lambda p: "A" if p >= 90 else "B" if p >= 75 else "C" if p >= 60 else "D"
    )

    await result_collection.insert_many(df.to_dict(orient="records"))

    return {
        "message": "Marks uploaded successfully",
        "count": len(df)
    }
async def upload_marks(
    file: UploadFile = File(...),
    max_marks_per_subject: int = Query(100)
):
    # ✅ File type validation
    if not file.filename.endswith((".xlsx", ".csv")):
        raise HTTPException(status_code=400, detail="Only Excel or CSV files allowed")

    # ✅ Read file
    df = (
        pd.read_excel(file.file)
        if file.filename.endswith(".xlsx")
        else pd.read_csv(file.file)
    )

    # ✅ Normalize column names
    df.columns = df.columns.str.strip().str.lower()

    if "email" not in df.columns:
        raise HTTPException(status_code=400, detail="Missing Email column")

    # ✅ Subject columns
    excluded = {"email", "student_email", "total", "percentage", "grade"}
    subject_cols = [c for c in df.columns if c not in excluded]

    if not subject_cols:
        raise HTTPException(status_code=400, detail="No subject columns found")

    valid_records = []

    # ✅ Validate students via USERS collection
    for _, row in df.iterrows():
        email = row["email"]

        user = await user_collection.find_one({
            "email": email,
            "role": "Student"
        })

        if not user:
            continue  # skip invalid student

        record = {subject: row[subject] for subject in subject_cols}
        record["student_email"] = email
        valid_records.append(record)

    if not valid_records:
        raise HTTPException(status_code=400, detail="No valid students found")

    df = pd.DataFrame(valid_records)

    # ✅ Convert marks to numeric
    for col in subject_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["total"] = df[subject_cols].sum(axis=1)
    total_max = len(subject_cols) * max_marks_per_subject
    df["percentage"] = (df["total"] / total_max * 100).round(2)

    df["grade"] = df["percentage"].apply(
        lambda p: "A" if p >= 90 else "B" if p >= 75 else "C" if p >= 60 else "D"
    )

    await result_collection.insert_many(df.to_dict(orient="records"))

    return {
        "message": "Marks uploaded successfully",
        "count": len(df)
    }




# ==============================
# 📌 DOWNLOAD RESULT API (download by student on there portal)

@router.get("/download")
async def download_result(email: str):
    student = await result_collection.find_one({"student_email": email})

    if not student:
        raise HTTPException(status_code=404, detail="Result not found")

    os.makedirs("results", exist_ok=True)
    safe_email = email.replace("@", "_").replace(".", "_")
    pdf_path = f"results/{safe_email}_result.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    elements = []

    # =====================
    # 🏫 INSTITUTE HEADER
    # =====================
    institute_style = ParagraphStyle(
        "InstituteTitle",
        fontSize=18,
        alignment=1,
        spaceAfter=10,
        textColor=colors.darkblue,
        bold=True
    )

    elements.append(Paragraph("KDK College of Engineering", institute_style))
    elements.append(Paragraph("Official Student Marksheet", styles["Italic"]))
    elements.append(Spacer(1, 20))

    # =====================
    # 👤 STUDENT DETAILS
    # =====================
    details = f"""
    <b>Email:</b> {student.get('student_email')}<br/>
    <b>Result Status:</b> PASS
    """
    elements.append(Paragraph(details, styles["Normal"]))
    elements.append(Spacer(1, 20))

    # =====================
    # 📚 SUBJECT TABLE
    # =====================
    table_data = [
        ["Subject", "Marks Obtained", "Max Marks"]
    ]

    subjects = ["math", "science", "english"]
    max_marks = 100

    for sub in subjects:
        table_data.append([
            sub.capitalize(),
            student.get(sub, 0),
            max_marks
        ])

    table = Table(table_data, colWidths=[2.5*inch, 2*inch, 2*inch])

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))

    # =====================
    # 📊 SUMMARY
    # =====================
    summary = f"""
    <b>Total Marks:</b> {student.get('total')}<br/>
    <b>Percentage:</b> {student.get('percentage')}%
    """
    elements.append(Paragraph(summary, styles["Normal"]))
    elements.append(Spacer(1, 10))

    # =====================
    # 🟢 GRADE (GREEN)
    # =====================
    grade_style = ParagraphStyle(
        "GradeStyle",
        fontSize=14,
        textColor=colors.green,
        spaceAfter=20,
        bold=True
    )

    elements.append(
        Paragraph(f"Grade: {student.get('grade')}", grade_style)
    )

    # =====================
    # ✍️ FOOTER
    # =====================
    elements.append(Spacer(1, 40))
    elements.append(Paragraph("Authorized Signature", styles["Normal"]))
    elements.append(Paragraph("Controller of Examination", styles["Italic"]))

    doc.build(elements)

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename="marksheet.pdf"
    )

   

# ==============================
# 📌 RESULT ANALYTICS API (view by admin on there portal)
@router.get("/analytics")
async def get_result_analytics():
    results = []
    cursor = result_collection.find({})

    async for r in cursor:
        r["_id"] = str(r["_id"])
        r["percentage"] = float(r.get("percentage", 0))
        results.append(r)

    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    percentages = [r["percentage"] for r in results]
    avg_percentage = sum(percentages) / len(percentages)

    toppers = sorted(
        results, key=lambda r: r["percentage"], reverse=True
    )[:3]

    return {
        "total_students": len(results),
        "average_percentage": round(avg_percentage, 2),
        "top_students": toppers,
    }
