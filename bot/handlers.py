import sys
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from retrieval.retriever import get_relevant_chunks
from rag.generator import generate_answer

logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 4000


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "☕ Selamat datang di Coffee AI Assistant!\n\n"
        "Saya adalah asisten kopi yang siap membantu Anda dengan:\n"
        "- Informasi tentang kopi\n"
        "- Metode penyeduhan\n"
        "- Varietas biji kopi\n"
        "- Budaya kopi\n\n"
        "Ketik pertanyaan Anda atau gunakan /help untuk melihat command yang tersedia."
    )
    await update.message.reply_text(welcome)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Command yang tersedia:\n\n"
        "/start - Mulai bot dan lihat pesan selamat datang\n"
        "/help - Tampilkan bantuan ini\n"
        "/n8n - Kirim pertanyaan terakhir ke n8n workflow\n\n"
        "Ketik pertanyaan bebas untuk chat dengan Coffee AI!"
    )
    await update.message.reply_text(help_text)


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = update.message.text
    logger.info(f"Chat from {update.effective_user.first_name}: {question}")

    try:
        await update.message.chat.send_action(action=ChatAction.TYPING)

        context.user_data["last_question"] = question

        chunks = get_relevant_chunks(question)

        if not chunks:
            await update.message.reply_text(
                "Maaf, saya belum memiliki pengetahuan yang cukup untuk menjawab pertanyaan ini. "
                "Coba tanyakan hal lain tentang kopi!"
            )
            return

        answer = generate_answer(question, chunks)

        if len(answer) > MAX_MESSAGE_LENGTH:
            answer = answer[:MAX_MESSAGE_LENGTH] + "\n\n... (jawaban dipotong)"

        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Error in chat: {e}", exc_info=True)
        await update.message.reply_text(
            f"Terjadi kesalahan: {str(e)}"
        )


async def send_to_n8n(update: Update, context: ContextTypes.DEFAULT_TYPE):
    import httpx
    from config import N8N_WEBHOOK_URL

    if not N8N_WEBHOOK_URL:
        await update.message.reply_text("N8N webhook URL belum dikonfigurasi.")
        return

    question = context.user_data.get("last_question", "")

    if not question:
        await update.message.reply_text("Belum ada pertanyaan untuk dikirim ke n8n.")
        return

    await update.message.reply_text("Mengirim ke n8n...")

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
            await update.message.reply_text(answer)
        else:
            await update.message.reply_text(f"Gagal: {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")
