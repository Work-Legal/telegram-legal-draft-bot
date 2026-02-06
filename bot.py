import os
import re
import pdfplumber
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PORT = int(os.environ.get("PORT", 8080))

# Load case numbers
def load_cases():
    with open("cases.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# Extract text from PDF
def extract_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Find court hall near case number
def find_court_hall(text, case_no):
    pattern = case_no + r".{0,200}"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        snippet = match.group()
        hall = re.search(
            r"(Court\s*Hall\s*No\.?\s*\d+|CH-\d+|Bench\s*\d+)",
            snippet,
            re.IGNORECASE
        )
        if hall:
            return hall.group()
    return "Court hall not clearly mentioned"

# Handle PDF
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    file = await doc.get_file()
    pdf_path = "causelist.pdf"
    await file.download_to_drive(pdf_path)

    await update.message.reply_text("📄 Causelist received. Checking your cases...")

    text = extract_text(pdf_path)
    cases = load_cases()

    found = False
    reply = "🔍 Cases Found:\n\n"

    for case in cases:
        if case.lower() in text.lower():
            found = True
            hall = find_court_hall(text, case)
            reply += f"✅ {case}\n🏛 {hall}\n\n"

    if not found:
        reply = "❌ None of your cases are listed today."

    await update.message.reply_text(reply)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

    # Webhook mode (Railway-safe)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=os.environ.get("WEBHOOK_URL"),
    )

if __name__ == "__main__":
    main()
