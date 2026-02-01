from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_answers_pdf(answers, out_path, subject):
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 60, f"Answer Key - {subject}")

    y = height - 100
    for a in answers:
        c.setFont('Helvetica', 12)
        c.drawString(40, y, f"Q{a['id']} - {a['answer']}")
        y -= 20
        if y < 60:
            c.showPage()
            y = height - 60
    c.save()
