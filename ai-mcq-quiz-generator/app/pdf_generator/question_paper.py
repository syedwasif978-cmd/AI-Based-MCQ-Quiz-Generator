from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def generate_questions_pdf(questions, out_path, subject, difficulty, time_limit=None):
    c = canvas.Canvas(out_path, pagesize=A4)
    width, height = A4
    c.setFont('Helvetica-Bold', 16)
    c.drawString(40, height - 60, f"Question Paper - {subject}")
    c.setFont('Helvetica', 10)
    c.drawString(40, height - 80, f"Difficulty: {difficulty}   Time: {time_limit or 'N/A'}")

    y = height - 120
    for q in questions:
        c.setFont('Helvetica-Bold', 11)
        c.drawString(40, y, f"Q{q['id']}. {q['q']}")
        y -= 20
        opts = q.get('options', [])
        for i, opt in enumerate(opts):
            label = chr(65 + i)
            c.setFont('Helvetica', 10)
            c.drawString(60, y, f"{label}) {opt}")
            y -= 16
        y -= 8
        if y < 80:
            c.showPage()
            y = height - 60
    c.save()
