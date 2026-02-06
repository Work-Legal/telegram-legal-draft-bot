import pdfplumber
import re
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# Load your case numbers
def load_cases():
    with open("cases.txt", "r") as f:
        return [line.strip() for line in f if line.strip()]

# Extract text from PDF
def extract_text_from_pdf(file_path):
    full_text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text

# Try to find court hall near case number
def find_court_hall(text, case_no):
    pattern = case_no + r".{0,200}"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        snippet = match.group()
        hall_match = re.search(r"(Court\s*Hall\s*No\.?\s*\d+|CH-\d+)", snippet, re.IGNORECASE)
        if hall_match:
            return hall_match.group()
    return "Court hall not clearly mentioned"

# Handle incoming PDF
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    if not document.file_name.lower().endswith(".pdf"):
        await update.message.reply_text("Please send a PDF causelist.")
        return

    file = await document.get_file()
    file_path = "causelist.pdf"
    await file.download_to_drive(file_path)

    await update.message.reply_text("📄 Causelist received. Checking your cases...")

    text = extract_text_from_pdf(file_path)
    cases = load_cases()

    found = False
    reply = "🔍 **Cases Found:**\n\n"

    for case in cases:
        if case.lower() in text.lower():
            found = True
            hall = find_court_hall(text, case)
            reply += f"✅ Case: {case}\n🏛 {hall}\n\n"

    if not found:
        reply = "❌ None of your cases are listed in this causelist."

    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.run_polling()

if __name__ == "__main__":
    main()
