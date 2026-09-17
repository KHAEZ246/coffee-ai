import os
import sys
import glob
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pdfplumber
import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import CHROMA_PERSIST_DIR, CHROMA_COLLECTION, CHUNK_SIZE, CHUNK_OVERLAP

def ingest_all():
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data"
    
    if not data_dir.exists():
        print(f"Directory {data_dir} tidak ditemukan!")
        return

    # Inisialisasi DB
    client = chromadb.PersistentClient(path=str(Path(CHROMA_PERSIST_DIR).absolute()))
    
    # Hapus collection lama jika ada, untuk memastikan data benar-benar bersih dan direplace
    try:
        client.delete_collection(name=CHROMA_COLLECTION)
        print(f"Collection lama '{CHROMA_COLLECTION}' telah dihapus.")
    except Exception:
        pass
        
    collection = client.create_collection(name=CHROMA_COLLECTION)
    
    # 1. Proses PDF
    pdf_dir = data_dir / "pdfs"
    if pdf_dir.exists():
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            is_separator_regex=False,
        )
        
        for pdf_path in pdf_files:
            file_name = pdf_path.name
            print(f"Memproses PDF: {file_name}...")
            full_text = ""
            
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text = page.extract_text()
                        if text:
                            full_text += text + "\n"
                            
                # Chunking
                chunks = text_splitter.create_documents(
                    texts=[full_text], 
                    metadatas=[{"source": file_name, "type": "pdf"}]
                )
                
                # Masukkan ke DB
                if chunks:
                    collection.add(
                        documents=[chunk.page_content for chunk in chunks],
                        metadatas=[chunk.metadata for chunk in chunks],
                        ids=[f"{file_name}_{i}" for i in range(len(chunks))]
                    )
                print(f"Berhasil memproses {len(chunks)} chunks dari {file_name}")
                
            except Exception as e:
                print(f"Error saat memproses PDF {file_name}: {e}")

    # 2. Proses Cookpad JSON
    cookpad_dir = data_dir / "cookpad"
    json_path = cookpad_dir / "resep_kopi.json"
    
    if json_path.exists():
        print(f"Memproses JSON Cookpad: {json_path.name}...")
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                recipes = json.load(f)
                
            docs = []
            metadatas = []
            ids = []
            
            for i, recipe in enumerate(recipes):
                judul = recipe.get("judul", "")
                bahan = "\n- ".join(recipe.get("bahan", []))
                langkah = "\n- ".join(recipe.get("langkah", []))
                
                # Gabungkan menjadi satu dokumen teks
                content = f"RESEP: {judul}\n\nBAHAN:\n- {bahan}\n\nCARA MEMBUAT:\n- {langkah}"
                
                docs.append(content)
                metadatas.append({"source": recipe.get("url", "cookpad"), "type": "recipe", "title": judul})
                ids.append(f"recipe_{i}")
                
            if docs:
                collection.add(
                    documents=docs,
                    metadatas=metadatas,
                    ids=ids
                )
            print(f"Berhasil memproses {len(docs)} resep dari Cookpad")
            
        except Exception as e:
            print(f"Error saat memproses JSON {json_path.name}: {e}")

    print("\nProses Ingestion Selesai! Semua data telah masuk ke ChromaDB.")


if __name__ == "__main__":
    ingest_all()
