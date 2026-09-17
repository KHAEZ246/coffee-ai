import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Kamu adalah asisten kopi. Jawab pertanyaan tentang kopi.

ATURAN FORMAT - WAJIB DIPATUHI:
1. JANGAN PERNAH pakai tabel markdown (|---|---|)
2. JANGAN PERNAH pakai heading markdown (###, ##, #)
3. JAWABAN MAXIMAL 500 KARAKTER

PAKAI HTML TAGS untuk formatting:
- <b>teks</b> untuk BOLD (judul, keyword, nama)
- <i>teks</i> untuk ITALIC (istilah asing, penekanan)
- <code>teks</code> untuk kode/angka penting
- JANGAN pakai tag lain selain ini

FORMAT DINAMIS - sesuaikan dengan konteks:
- BAHAN/INGREDIENTS → bullet pakai emoji, 1 item per baris
- LANGKAH-LANGKAH → numbered list (1. 2. 3.)
- DEFINISI/ISTILAH → <b>bold keyword</b> + penjelasan
- TIPS → emoji bullet dengan <b>bold</b>
- JANGAN gabung semua jadi 1 kalimat panjang
- Gunakan spasi/baris kosong untuk memisahkan section

ATURAN LAIN:
- Jawab dalam bahasa yang sama dengan pertanyaan
- Kalau tidak yakin, bilang saja tidak tahu
- JANGAN jawab pertanyaan di luar kopi. Tolak dengan: "Maaf, saya hanya bisa menjawab pertanyaan seputar kopi."
- Kalau ditanya resep, kasih bahan + langkah pakai format di atas"""


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    context = "\n\n".join([chunk["content"] for chunk in context_chunks])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Konteks dari basis pengetahuan:\n\n{context}\n\nPertanyaan: {question}"}
    ]

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python -m rag.generator <question>")
        sys.exit(1)

    question = sys.argv[1]
    from retrieval.retriever import get_relevant_chunks
    chunks = get_relevant_chunks(question)

    if not chunks:
        print("No relevant chunks found.")
        sys.exit(1)

    answer = generate_answer(question, chunks)
    print(f"Q: {question}")
    print(f"A: {answer}")
