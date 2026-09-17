import os
import glob
import pdfplumber
from langchain_text_splitters import RecursiveCharacterTextSplitter

def parse_pdfs(data_dir: str):
    pdf_files = glob.glob(os.path.join(data_dir, "*.pdf"))
    if not pdf_files:
        print(f"Tidak ada file PDF yang ditemukan di {data_dir}")
        return

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        length_function=len,
        is_separator_regex=False,
    )

    all_chunks = []

    for pdf_path in pdf_files:
        file_name = os.path.basename(pdf_path)
        print(f"Memproses {file_name}...")
        full_text = ""
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
                        
            # Lakukan chunking
            chunks = text_splitter.create_documents(
                texts=[full_text], 
                metadatas=[{"source": "pdf", "file_name": file_name}]
            )
            all_chunks.extend(chunks)
            
            print(f"Berhasil membuat {len(chunks)} chunks dari {file_name}.")
            
        except Exception as e:
            print(f"Error saat memproses {file_name}: {e}")

    print(f"\nTotal chunks keseluruhan: {len(all_chunks)}")
    
    # Menampilkan 2 contoh chunk pertama
    if all_chunks:
        print("\nContoh Chunk:")
        for i, chunk in enumerate(all_chunks[:2]):
            print(f"\n--- Chunk {i+1} ---")
            print(f"Metadata: {chunk.metadata}")
            print(f"Text preview: {chunk.page_content[:100]}...")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_dir = os.path.join(os.path.dirname(current_dir), "data", "pdfs")
    
    # Pastikan folder ada
    os.makedirs(pdf_dir, exist_ok=True)
    
    parse_pdfs(pdf_dir)
