import os
import shutil
import pandas as pd
from autogen import AssistantAgent, UserProxyAgent

# --- 1. KONFIGURASI ---
config_list = [{"model": "kost_coder", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]
llm_config = {"config_list": config_list, "cache_seed": None, "temperature": 0}

work_dir = "coding"
if not os.path.exists(work_dir): os.makedirs(work_dir)

nama_file = "data_kos.csv" 

# Setup File: Copy data ke folder eksekusi
if os.path.exists(nama_file):
    shutil.copy(nama_file, os.path.join(work_dir, nama_file))
    print(f"[SUCCESS] File '{nama_file}' siap di folder coding.")
elif not os.path.exists(os.path.join(work_dir, nama_file)):
    print(f"\n[ERROR] File '{nama_file}' tidak ditemukan!")
    exit()

# --- 2. DEFINISI AGEN ---

# Agen Eksekutor (Menjalankan Kode)
user_executor = UserProxyAgent(
    name="Executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=5,
    code_execution_config={"work_dir": work_dir, "use_docker": False},
)

# Agen Coder (Khusus Hard Constraint & Data)
data_assistant = AssistantAgent(
    name="Python_Coder",
    llm_config=llm_config,
    system_message=f"""
    Kamu adalah Python Data Scientist. Tugasmu HANYA menulis kode Python untuk memfilter data KERAS.
    
    ATURAN MUTLAK KODE:
    1. **Filter Keras:** Hanya filter kriteria 'ac', 'wifi', 'parkir', 'kamar mandi dalam', atau Nama Kota.
    2. **ABAIKAN Soft Constraint:** JANGAN memfilter kata 'tenang', 'nyaman', 'aman', atau 'bersih' di dalam kode.
    3. **Syntax Wajib:**
       - df = pd.read_csv('{nama_file}', sep=';')
       - Cleaning Harga: 
         df['p_c'] = df['price'].astype(str).str.replace('Rp','').str.replace('.','', regex=False).str.split('/').str[0].str.split(' ').str[0]
         df['price_final'] = pd.to_numeric(df['p_c'], errors='coerce')
         df = df.dropna(subset=['price_final'])
       - Filter Fasilitas: Gunakan `df['all_facilities_bs'].str.contains('keyword', case=False, na=False)`
       - Output: Tampilkan kolom [room_name, region, price, all_facilities_bs] dengan `.to_string(index=False)`.
    
    Hanya berikan kode dalam blok ```python. JANGAN berikan narasi penjelasan.
    """
)

# Agen Konsultan (Khusus Soft Constraint & Penalaran)
kost_consultant = AssistantAgent(
    name="Consultant",
    llm_config=llm_config,
    system_message="""
    Kamu adalah Konsultan Properti Kos. Tugasmu memberikan evaluasi subjektif (soft constraint).
    
    Tugasmu:
    1. Baca tabel hasil yang diberikan.
    2. Analisis mana kos yang paling sesuai dengan permintaan subjektif user (seperti 'tenang', 'strategis', atau 'bersih').
    3. Gunakan logika heuristik: misalnya, kos di 'perumahan' lebih tenang daripada di 'jalan raya'.
    
    Format: Berikan narasi ramah dalam Bahasa Indonesia. Akhiri dengan "TERMINATE".
    """
)

# --- 3. ALUR KERJA (SEQUENTIAL CHAT) ---

print("\n" + "="*60)
print("SISTEM REKOMENDASI KOS: HARD & SOFT CONSTRAINT")
print("="*60)
request = input("\nMasukkan kriteria kos Anda: ")

# LANGKAH 1: Filter Data (Hard Constraint)
print("\n[LOG] Langkah 1: Memproses Kriteria Fasilitas & Harga...")
coder_chat = user_executor.initiate_chat(
    data_assistant, 
    message=f"Tulis kode untuk mencari kriteria keras: {request}",
    silent=False
)

# Ambil output tabel murni dari terminal
last_msg = user_executor.last_message(data_assistant)["content"]
if "Code output:" in last_msg:
    hard_data = last_msg.split("Code output:")[1].strip()
else:
    hard_data = ""

# LANGKAH 2: Analisis Subjektif (Soft Constraint)
if "Empty DataFrame" in hard_data or not hard_data:
    print("\n[HASIL] Tidak ditemukan kos yang cocok dengan kriteria fasilitas/harga tersebut.")
else:
    print("\n" + "-"*60)
    print("[LOG] Langkah 2: Menganalisis Suasana & Kenyamanan...")
    print("-"*60)
    
    kost_consultant.initiate_chat(
        user_executor,
        message=f"""
        Permintaan User: {request}
        
        Berikut adalah daftar kos yang cocok secara fasilitas:
        {hard_data}
        
        Berdasarkan data tersebut, tolong rekomendasikan mana yang paling cocok dengan kriteria subjektif user (misal: ketenangan/kenyamanan).
        """
    )