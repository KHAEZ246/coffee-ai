import os
import json
import time
import requests
import concurrent.futures
from bs4 import BeautifulSoup

# Gunakan Session global agar koneksi HTTP bisa di-reuse oleh threads
session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
session.headers.update(headers)

banned_words = ['cake', 'kue', 'bolu', 'roti', 'pudding', 'cookies', 'brownies', 'pie', 'tart', 'muffin', 'bread', 'sourdough',
    'puding', 'jelly', 'toast', 'es krim', 'donat', 'cendol', 'snack', 'ice cream', 'cokelat', 'permen', 'ongol-ongol', 'coffee cream',
    'brownis', 'biscoff', 'brudel', 'tamblag', 'kukis', 'sagu', 'tape', 'puding', 'gelatin', 'nutrijell', 'brudel', 'biji ketapang',
    'cumi', 'putu', 'chiffon', 'gabin', 'sambal', 'dessert', 'cekodok', 'popcorn', 'selai', 'chicken', 'makanan', 'ikan', 'pasta',
    'granola', 'churros', 'bacem', 'serabi', 'steak', 'pastry', 'custard', 'flan', 'kembang goyang', 'bakpao', 'samosa', 'waffle',
    'risol', 'lumpia', 'kebab', 'ramen', 'udang', 'ketoprak', 'nasi goreng', 'pizza', 'dorayaki', 'martabak', 'kahlua', 'brulee',
    'labu', 'tahu', 'lapis', 'cassava', 'cucur', 'manisan', 'cemilan', 'talam', 'kukus', 'Klappertaart', 'goreng', 'crispy', 'getuk',
    'ciffon', 'colenak', 'kinca', 'ongol', 'ongol ongol', 'ongol-ongol', 'carang', 'gesing', 'ladyfinger', 'ayam', 'babi', 'daging',
    'mochi', 'agar-agar', 'agar', 'kukus', 'es gabus', 'bakpia', 'rolls', 'kolak', 'soes', 'sayuran', 'ogura', 'bluder', 'batun', 'bedul',
    'spaghetti', 'spageti', 'cengkodok', 'klepon', 'moci', 'mousse', 'pukis', 'rawon', 'panggang', 'semprong', 'bun', 'pop corn',
    'semprit']

def fetch_recipe_detail(full_url: str):
    """Fungsi pembantu untuk mengambil detail resep satu per satu."""
    try:
        # Sedikit jeda acak/singkat di dalam thread sangat membantu menghindari blokir agresif
        time.sleep(0.5)
        
        res = session.get(full_url, timeout=10)
        res.raise_for_status()
        recipe_soup = BeautifulSoup(res.text, 'html.parser')
        
        title_tag = recipe_soup.select_one("h1")
        title = title_tag.text.strip() if title_tag else "Tanpa Judul"
        
        title_lower = title.lower()
        if any(banned_word in title_lower for banned_word in banned_words):
            return {"status": "skip", "title": title, "url": full_url, "reason": "Makanan"}
        
        ingredients = []
        for item in recipe_soup.select(".ingredient-list li, [itemprop='recipeIngredient']"):
            ingredients.append(item.text.strip())
            
        steps = []
        for step in recipe_soup.select(".step, [itemprop='recipeInstructions']"):
            steps.append(step.text.strip())
            
        return {
            "status": "ok",
            "title": title,
            "data": {
                "url": full_url,
                "judul": title,
                "bahan": ingredients,
                "langkah": steps,
                "source": "cookpad"
            }
        }
    except Exception as e:
        return {"status": "error", "title": "Error", "url": full_url, "reason": str(e)}

def scrape_cookpad_kopi(output_dir: str, target_count: int = 100):
    recipes_data = []
    page = 1
    
    print(f"Memulai scraping mode MULTITHREAD... Target: {target_count} resep.")
    
    while len(recipes_data) < target_count:
        search_url = f"https://cookpad.com/id/cari/kopi?page={page}"
        print(f"\n--- Mengambil Halaman {page} ---")
        
        try:
            response = session.get(search_url, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print(f"Error mengakses halaman {page}: {e}")
            break
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        recipe_links = []
        for a_tag in soup.select('a[href^="/id/resep/"]'):
            href = a_tag.get('href')
            if href and href not in recipe_links and not href.endswith('/baru'):
                recipe_links.append(f"https://cookpad.com{href}")
                
        if not recipe_links:
            print("Tidak ada link resep lagi yang ditemukan (kemungkinan halaman sudah habis).")
            break
            
        print(f"Ditemukan {len(recipe_links)} link resep di Halaman {page}. Memulai ekstraksi paralel...")
        
        # Eksekusi secara paralel (multithreading)
        # Max workers 5 artinya mengambil 5 halaman detail sekaligus. Jangan terlalu besar agar tidak kena 504.
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Petakan link ke fungsi fetch_recipe_detail
            futures = [executor.submit(fetch_recipe_detail, url) for url in recipe_links]
            
            for future in concurrent.futures.as_completed(futures):
                if len(recipes_data) >= target_count:
                    # Batal sisa eksekusi jika target sudah tercapai
                    executor.shutdown(wait=False, cancel_futures=True)
                    break
                    
                result = future.result()
                
                if result["status"] == "ok":
                    recipes_data.append(result["data"])
                    print(f"  [OK] ({len(recipes_data)}/{target_count}) {result['title']}")
                elif result["status"] == "skip":
                    print(f"  [SKIP] ({result['reason']}): {result['title']}")
                else:
                    print(f"  [ERROR] {result['url']}: {result['reason']}")

        page += 1
        
        if len(recipes_data) < target_count:
            print("Menunggu 3 detik sebelum halaman pencarian berikutnya...")
            time.sleep(3)

    output_path = os.path.join(output_dir, "resep_kopi.json")
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(recipes_data, f, ensure_ascii=False, indent=4)
        print(f"\nSelesai! Berhasil menyimpan {len(recipes_data)} resep kopi ke {output_path}")
    except Exception as e:
        print(f"Error menyimpan JSON: {e}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    cookpad_dir = os.path.join(os.path.dirname(current_dir), "data", "cookpad")
    
    os.makedirs(cookpad_dir, exist_ok=True)
    scrape_cookpad_kopi(cookpad_dir, target_count=1000)
