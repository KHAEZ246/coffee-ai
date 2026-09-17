# Coffee AI Assistant

Telegram bot RAG (Retrieval-Augmented Generation) untuk pengetahuan kopi.

## Features

- Chatbot Telegram dengan basis pengetahuan kopi
- PDF ingestion untuk menambah pengetahuan
- ChromaDB untuk vector storage
- Groq API untuk generasi jawaban
- n8n integration untuk workflow automation

## Tech Stack

- Python 3.11+
- uv (package manager)
- python-telegram-bot
- ChromaDB
- Groq API
- pypdf

## Installation

1. Clone repo:
```bash
git clone https://github.com/yourusername/coffee-ai.git
cd coffee-ai
```

2. Install dependencies:
```bash
uv sync
```

3. Setup environment:
```bash
cp .env.example .env
```

4. Edit `.env` dengan API keys Anda:
```
GROQ_API_KEY=gsk_your_key
TELEGRAM_BOT_TOKEN=your_token
```

## Usage

### Ingest PDF

```bash
uv run python -m ingestion.ingest path/to/coffee.pdf
```

### Run Bot

```bash
uv run python main.py
```

### Test Retrieval

```bash
uv run python -m retrieval.retriever "bagaimana cara menyeduh kopi"
```

### Test RAG

```bash
uv run python -m rag.generator "apa itu espresso"
```

## Bot Commands

- `/start` - Mulai bot
- `/help` - Lihat command
- `/n8n` - Kirim ke n8n workflow
- Ketik pesan - Chat dengan AI

## Project Structure

```
coffee-ai/
├── main.py                 # Entry point
├── config.py               # Configuration
├── .env.example            # Environment template
├── ingestion/
│   └── ingest.py           # PDF → ChromaDB
├── retrieval/
│   └── retriever.py        # Similarity search
├── rag/
│   └── generator.py        # Groq API integration
├── bot/
│   └── handlers.py         # Telegram handlers
└── n8n/
    └── workflows/
        └── coffee-assistant.json
```

## License

MIT
