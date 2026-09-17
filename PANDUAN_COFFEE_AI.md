# ☕ Panduan Lengkap Coffee AI (RAG Telegram Bot)

Dokumen ini adalah panduan lengkap (*cheatsheet*) untuk menjalankan seluruh komponen dari proyek **Coffee AI**, mulai dari pengambilan data (scraping) hingga menjalankan chatbot Telegram.

Pastikan kamu selalu berada di dalam folder `main/coffee-ai` saat menjalankan perintah-perintah di bawah ini:
```bash
cd "d:\A iim\KULIAH\SEM 5\NLP\Tugas\RAG\main\coffee-ai"
```

---

## 1. Persiapan Awal (Environment)

Pastikan file `.env` kamu sudah terisi dengan benar. Jika belum, buat file `.env` dan isi dengan konfigurasi berikut:

```env
GROQ_API_KEY=gsk_kunci_api_groq_kamu
TELEGRAM_BOT_TOKEN=token_bot_telegram_kamu
# Jika ada API key lain (seperti Supabase) biarkan saja, tapi saat ini kita pakai ChromaDB lokal.
```

---

## 2. Mengumpulkan Data (Scraping)
*Hanya jalankan perintah ini jika kamu ingin mengambil data resep baru dari internet.*

Jika kamu ingin memperbarui isi dari `data/cookpad/resep_kopi.json`, jalankan script scraper Cookpad:
```bash
uv run python ingestion/scrape_cookpad.py
```
> **Catatan:** Script ini menggunakan sistem *multithreading* dan *delay* sehingga bisa mendownload ratusan resep secara otomatis namun tetap aman dari pemblokiran (error 504).

---

## 3. Memasukkan Data ke Otak AI (Ingestion)
*Jalankan perintah ini setiap kali kamu menambahkan file PDF baru di folder `data/pdfs/` atau mengupdate `resep_kopi.json`.*

Proses ini akan membaca semua teks, memotongnya menjadi *chunk* kecil, mengubahnya jadi vektor, dan memasukkannya ke ChromaDB lokal:
```bash
uv run python ingestion/ingest.py
```
> **Catatan:** Proses ini otomatis menghapus ingatan lama dan menggantinya dengan yang baru. Saat pertama kali dijalankan, sistem akan mendownload model *embedding* `all-MiniLM-L6-v2` (sekitar 79MB).

---

## 4. Mode Pengujian (Testing)
Kamu bisa mengetes kemampuan AI tanpa harus menyalakan bot Telegram. Ini sangat berguna untuk mencari tahu apakah sistem mengambil informasi yang benar atau tidak.

### A. Uji Coba Pencarian Saja (Retrieval)
Gunakan ini untuk mengecek apakah sistem menemukan dokumen/resep yang relevan di database:
```bash
uv run python -m retrieval.retriever "apa itu espresso?"
```

### B. Uji Coba Menjawab (Generator / RAG)
Gunakan ini untuk mengecek kemampuan LLM (Groq) dalam merangkum hasil pencarian menjadi jawaban yang luwes:
```bash
uv run python -m rag.generator "bagaimana cara membuat dalgona coffee?"
```
*(Catatan Windows: Jika muncul error `UnicodeEncodeError` di terminal saat mengetes generator, abaikan saja. Itu hanya isu tampilan font emoji di terminal Windows. Di Telegram dijamin aman!)*

---

## 5. Menjalankan Chatbot Telegram (Produksi)
Langkah terakhir! Jika semuanya sudah siap, nyalakan mesin bot Telegram agar bisa diajak *chatting* oleh *user*:
```bash
uv run python main.py
```

Setelah terminal memunculkan tulisan `Coffee AI Bot is running...`, silakan buka Telegram dan chat bot kamu.

**Perintah Dasar Bot Telegram:**
- `/start` - Memulai percakapan dengan bot.
- `/help` - Melihat bantuan.
- *(Ketik pesan apapun)* - Bot akan otomatis menjawab menggunakan pengetahuan dari RAG.

> [!WARNING]
> **Peringatan Bentrok Bot:** Jika kamu bekerja secara tim, **jangan** menjalankan `uv run python main.py` secara bersamaan dengan temanmu menggunakan Token Bot Telegram yang sama! Nanti pesannya akan terpencar (rebutan). Sebaiknya bergantian, atau buat Token Bot baru khusus untuk testing di laptopmu melalui **@BotFather** di Telegram.
