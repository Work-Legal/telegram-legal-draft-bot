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

# Environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Fixed master prompt (LOCKED BEHAVIOUR)
MASTER_PROMPT = """
You are a conservative Indian civil court advocate.

You must draft ONLY:
1) Interlocutory Application
2) Supporting Affidavit

STRICT RULES:
- Follow the given format exactly
- Do not change headings or sequence
- Do not invent facts
- Do not add case law
- Reasoning must be brief, routine, and procedural
- Language must be formal and restrained
- Draft only the BODY portion

Use only the facts provided by the user.
"""

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Legal Draft Bot is running.\n\n"
        "Use /ia to draft IA + Affidavit."
    )

# /ia command (instruction step)
async def ia_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["awaiting_ia_details"] = True

    await update.message.reply_text(
        "📄 IA Drafting Mode\n\n"
        "Send details EXACTLY in this format:\n\n"
        "Case Number:\n"
        "Court Name:\n"
        "Applicant:\n"
        "Opponent:\n"
        "Purpose of IA:\n"
        "Reason (1–2 lines):"
    )

# Handle IA input + OpenAI drafting
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_ia_details"):
        user_input = update.message.text

        prompt = f"""
{MASTER_PROMPT}

FACTS PROVIDED BY USER:
{user_input}

Draft the IA body first, then the affidavit body.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": MASTER_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.2
            )

            draft_text = response.choices[0].message.content

            await update.message.reply_text(
                "🧾 Draft IA + Affidavit (Body Portion):\n\n"
                f"{draft_text}"
            )

            context.user_data.clear()

        except Exception as e:
            await update.message.reply_text(
                "❌ Error while drafting. Please try again."
            )
            print(e)
    else:
        await update.message.reply_text(
            "Use /ia to start drafting."
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ia", ia_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
