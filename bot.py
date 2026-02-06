import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

MASTER_PROMPT = """
You are a conservative Indian civil court advocate.

You must draft ONLY:
1) Interlocutory Application
2) Supporting Affidavit

RULES:
- Follow the given format strictly
- Do not add case law
- Do not invent facts
- Reasoning must be brief and procedural
- Language must be formal and restrained
- Draft only the BODY portion
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Legal Draft Bot is running.\nUse /ia to draft IA + Affidavit."
    )

async def ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["awaiting"] = True
    await update.message.reply_text(
        "Send IA details in plain text:\n\n"
        "Case Number:\nCourt Name:\nApplicant:\nOpponent:\n"
        "Purpose of IA:\nReason (1–2 lines):"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting"):
        await update.message.reply_text("Use /ia to start.")
        return

    user_input = update.message.text

    try:
        response = client.responses.create(
            model="gpt-3.5-turbo",
            input=f"{MASTER_PROMPT}\n\nFACTS:\n{user_input}"
        )

        draft_text = response.output_text

        await update.message.reply_text(
            "🧾 Draft (IA + Affidavit Body):\n\n" + draft_text
        )

        context.user_data.clear()

    except Exception as e:
        # 🔥 SHOW REAL ERROR IN TELEGRAM
        await update.message.reply_text(
            f"❌ OPENAI ERROR:\n{str(e)}"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ia", ia_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()
