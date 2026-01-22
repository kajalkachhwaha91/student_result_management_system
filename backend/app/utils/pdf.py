from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime


def generate_bonafide_pdf(data: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Times-Bold", 16)
    pdf.drawCentredString(width / 2, height - 100, "BONAFIDE CERTIFICATE")

    pdf.setFont("Times-Roman", 12)

    text = pdf.beginText(80, height - 160)
    text.textLine(
        f"This is to certify that {data['name']} "
        f"(Enrollment No: {data['enrollment']}) "
        f"is a bonafide student of {data['course']} "
        f"for the academic year {data['year']}."
    )
    text.textLine("")
    text.textLine(f"This certificate is issued for the purpose of:")
    text.textLine(f"{data['reason']}")
    text.textLine("")
    text.textLine(f"Date: {data['date']}")

    pdf.drawText(text)

    pdf.drawString(width - 200, 120, "Authorized Signatory")

    pdf.showPage()
    pdf.save()

    buffer.seek(0)
    return buffer.read()
