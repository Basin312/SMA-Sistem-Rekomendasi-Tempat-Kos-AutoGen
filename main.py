import os
import shutil
import pandas as pd
from autogen import AssistantAgent, UserProxyAgent

# --- CONFIG ---
config_list = [{"model": "kost_coder", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]
llm_config = {"config_list": config_list, "cache_seed": None, "temperature": 0}

# --- SETUP FILE ---
work_dir = "coding"
if not os.path.exists(work_dir): os.makedirs(work_dir)

# NAMA FILE BARU (Yang lebih simpel)
nama_file = "data_kos.csv" 

# Cek & Copy Otomatis
# KITA HAPUS BAGIAN COPY OTOMATIS JIKA ANDA INGIN MENGUJI SOLUSI MANUAL (PILAR 2)
# Untuk saat ini, kita biarkan saja dulu untuk melihat apakah PILAR 2 berhasil.
if os.path.exists(nama_file):
    shutil.copy(nama_file, os.path.join(work_dir, nama_file))
    print(f"[SUCCESS] File '{nama_file}' ditemukan dan disalin ke folder coding.")
elif os.path.exists(os.path.join(work_dir, nama_file)):
    print(f"[INFO] File '{nama_file}' sudah ada di folder coding.")
else:
    print(f"\n[ERROR] File '{nama_file}' TIDAK DITEMUKAN di folder proyek!")
    print("Silakan Rename file asli menjadi 'data_kos.csv' dan taruh di sebelah main.py")
    exit()

# --- AGENTS ---
user_proxy = UserProxyAgent(
    name="user_executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    code_execution_config={"work_dir": work_dir, "use_docker": False},
)

data_assistant = AssistantAgent(
    name="kost_coder",
    llm_config=llm_config,
    system_message=f"""
    Kamu Python Data Scientist yang bertugas mencari kos. File: '{nama_file}'.

    ATURAN MUTLAK KODE:
    1. Pembacaan File: WAJIB gunakan `pd.read_csv('{nama_file}', sep=';')`.
    2. Blok kode harus diakhiri `print("TERMINATE")`.
    
    1. CLEANING HARGA:
        # Gunakan kolom 'price_final' untuk harga bersih.
        df['price_clean'] = df['price'].astype(str).str.replace('Rp','').str.replace('.','', regex=False).str.split('/').str[0].str.split(' ').str[0]
        df['price_final'] = pd.to_numeric(df['price_clean'], errors='coerce')
        df = df.dropna(subset=['price_final'])
        
    2. LOGIC FILTERING:
        - Fasilitas: Gunakan `df['all_facilities_bs'].str.contains('keyword', case=False, na=False)`
        - Termurah: Setelah filter, gunakan `.sort_values('price_final').head(N)` untuk mengambil N hasil termurah.
        
    3. OUTPUT:
        - Tampilkan tabel kolom: room_name, region, price, all_facilities_bs
        - WAJIB gunakan `.to_string(index=False)` untuk menampilkan hasil.
    """
)

# --- RUN ---
print("\n=======================================================")
print("SISTEM PENCARI KOS (FINAL FIX)")
print("=======================================================")
request = input("\nMasukkan pencarian (cth: kos murah ada wifi atau kos di Depok AC max 2 juta): ")
user_proxy.initiate_chat(data_assistant, message=f"Buatkan kode python. File: {nama_file}. Request: {request}")