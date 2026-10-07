import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = "generated_certificates"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_certificate(
    recipient_name: str,
    event_name: str,
    course_name: str,
    certificate_id: str
):

    file_path = os.path.join(
        OUTPUT_DIR,
        f"{certificate_id}.pdf"
    )

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        file_path,
        pagesize=landscape(A4)
    )

    pdf.setStrokeColor(colors.darkblue)
    pdf.setLineWidth(4)

    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60
    )

    pdf.setFont("Helvetica-Bold", 32)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 120,
        "CERTIFICATE OF COMPLETION"
    )

    pdf.setFont("Helvetica", 18)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 180,
        "This certificate is proudly presented to"
    )

    pdf.setFont("Helvetica-Bold", 28)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 240,
        recipient_name
    )

    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 290,
        f"for successfully completing {course_name}"
    )

    pdf.drawCentredString(
        page_width / 2,
        page_height - 320,
        f"Event: {event_name}"
    )

    pdf.setFont("Helvetica", 10)

    pdf.drawCentredString(
        page_width / 2,
        60,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return file_path


if __name__ == "__main__":

    print("Starting certificate generation...")

    path = generate_certificate(
        recipient_name="Rahul Kumar",
        event_name="Python Workshop 2026",
        course_name="Python Programming",
        certificate_id="test-certificate-001"
    )

    print("Certificate generated successfully!")
    print("File:", path)