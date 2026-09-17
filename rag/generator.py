import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL


client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Kamu adalah asisten kopi. Jawab pertanyaan tentang kopi.

ATURAN FORMAT - WAJIB DIPATUHI:
1. JANGAN PERNAH pakai tabel markdown (|---|---|)
2. JANGAN PERNAH pakai heading (###, ##, #)
3. JANGAN PERNAH pakai code block (```)
4. JANGAN PERNAH pakai format *bold* atau _italic_ berlebihan
5. PAKAI saja bullet point pakai - atau • dan emoji
6. Jawaban MAXIMAL 500 KARAKTER. Kalau terlalu panjang, RINGKAS.
7. Jawab dalam bahasa yang sama dengan pertanyaan
8. Kalau tidak yakin, bilang saja tidak tahu
9. JANGAN jawab pertanyaan yang TIDAK BERHUBUNGAN dengan kopi atau minuman. Jika ditanya hal di luar kopi atau tentang makanan, tolak dengan sopan: "Maaf Kak, aku cuma bisa bantu jawab seputar minuman kopi nih."
10. Gunakan gaya bahasa kasual, ramah, dan gaul. Selalu panggil pengguna dengan sebutan "Kak". """


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
