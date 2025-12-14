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
    Kamu adalah robot pembuat kode Python. HANYA tulis kode dalam blok ```python.

    # --- BAGIAN 1: DATA REFERENCE (Hard Constraint) ---
    Kolom yang tersedia: 'room_name', 'region', 'price', 'all_facilities_bs'.
    - Lokasi: kolom 'region'
    - Fasilitas: kolom 'all_facilities_bs'
    - Harga: kolom 'price' (harus dibersihkan dulu)

    # --- BAGIAN 2: INSTRUKSI KODE WAJIB ---
    1. Load: `df = pd.read_csv('{nama_file}', sep=';')`
    2. Clean Harga: `df['p_num'] = pd.to_numeric(df['price'].astype(str).str.replace(r'\\D', '', regex=True), errors='coerce').fillna(0)`
    
    # --- BAGIAN 3: LOGIKA PEMROSESAN (Hard & Soft) ---
    - HARD (Lakukan ini): 
        * Jika ada nama kota (Depok/Bogor/dll), gunakan `.str.contains` pada kolom 'region'.
        * Jika ada kata 'murah', gunakan `.sort_values(by='p_num', ascending=True)`.
        * Jika ada kata 'eksklusif', gunakan `.sort_values(by='p_num', ascending=False)`.
    - SOFT (Abaikan ini dalam kode):
        * Jika ada kata 'nyaman', 'tenang', 'strategis', JANGAN buat filter kode apapun. Abaikan saja.

    # --- BAGIAN 4: OUTPUT ---
    `print(df[['room_name', 'region', 'price', 'all_facilities_bs']].head(3).to_string(index=False))`
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
    print("\n[HASIL] Tidak ditemukan kos yang cocok. Coba kurangi kriteria Anda.")
else:
    print("\n" + "-"*60)
    print("[LOG] Langkah 2: Consultant sedang merangkum hasil...")
    print("-"*60)
    
    # Biarkan Consultant membaca tabel hasil dari Coder
    user_executor.initiate_chat(
        kost_consultant,
        message=f"""
        User mencari: {request}
        
        Hasil pencarian tabel:
        {hard_data}
        
        Tolong berikan rekomendasi singkat dan ramah dari 3 data di atas. 
        Sebutkan kelebihan fasilitasnya.
        """
    )