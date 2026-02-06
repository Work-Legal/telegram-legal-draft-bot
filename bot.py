import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
SYSTEM_PROMPT = """PASTE YOUR PHASE 3 MASTER PROMPT HERE"""

IA_TEMPLATE = """PASTE PHASE 1 IA TEMPLATE HERE"""
AFFIDAVIT_TEMPLATE = """PASTE PHASE 1 AFFIDAVIT TEMPLATE HERE"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send /ia and then paste case details and facts in bullet points."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text

    prompt = f"""
{SYSTEM_PROMPT}

TEMPLATE:
{IA_TEMPLATE}

{AFFIDAVIT_TEMPLATE}

USER INPUT:
{user_input}

Fill only the permitted placeholders.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    await update.message.reply_text(response.choices[0].message.content)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

app.run_polling()
