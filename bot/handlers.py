import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes

from retrieval.retriever import get_relevant_chunks
from rag.generator import generate_answer

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


async def send_reply(update: Update, text: str):
    try:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except Exception:
        await update.message.reply_text(escape_html(text))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "☕ <b>Selamat datang di Coffee AI Assistant!</b>\n\n"
        "Saya adalah asisten kopi yang siap membantu Anda dengan:\n"
        "• Informasi tentang kopi\n"
        "• Metode penyeduhan\n"
        "• Varietas biji kopi\n"
        "• Budaya kopi\n\n"
        "Ketik pertanyaan Anda atau gunakan /help untuk melihat command yang tersedia."
    )
    await send_reply(update, welcome)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 <b>Command yang tersedia:</b>\n\n"
        "/start - Mulai bot\n"
        "/help - Tampilkan bantuan\n"
        "/n8n - Kirim ke n8n workflow\n\n"
        "Ketik pertanyaan bebas untuk chat dengan Coffee AI!"
    )
    await send_reply(update, help_text)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    logger.info(f"Chat from {update.effective_user.first_name}: {question}")

    try:
        await update.message.chat.send_action(action=ChatAction.TYPING)

        context.user_data["last_question"] = question

        chunks = get_relevant_chunks(question)

        if not chunks:
            await send_reply(update,
                "Maaf, saya belum memiliki pengetahuan yang cukup untuk menjawab pertanyaan ini. "
                "Coba tanyakan hal lain tentang kopi!"
            )
            return

        answer = generate_answer(question, chunks)

        if len(answer) > MAX_MESSAGE_LENGTH:
            answer = answer[:MAX_MESSAGE_LENGTH] + "\n\n... (jawaban dipotong)"

        await send_reply(update, answer)

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        await send_reply(update, f"Terjadi kesalahan: {escape_html(str(e))}")


async def send_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import httpx
    from config import N8N_WEBHOOK_URL

    if not N8N_WEBHOOK_URL:
        await send_reply(update, "N8N webhook URL belum dikonfigurasi.")
        return

    question = context.user_data.get("last_question", "")

    if not question:
        await send_reply(update, "Belum ada pertanyaan untuk dikirim ke n8n.")
        return

    await send_reply(update, "Mengirim ke n8n...")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                N8N_WEBHOOK_URL,
                json={"question": question},
                timeout=30.0
            )

        if response.status_code == 200:
            data = response.json()
            answer = data.get("answer", data.get("message", str(data)))
            await send_reply(update, answer)
        else:
            await send_reply(update, f"Gagal: {response.status_code}")

    except Exception as e:
        await send_reply(update, f"Error: {escape_html(str(e))}")
