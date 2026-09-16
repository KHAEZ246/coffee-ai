import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY belum ditemukan di file .env")

client = Groq(api_key=api_key)

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": (
                "You are a technical coffee assistant. "
                "Answer clearly and accurately."
            ),
        },
        {
            "role": "user",
            "content": "Jelaskan secara singkat apa itu espresso.",
        },
    ],
)

print(response.choices[0].message.content)