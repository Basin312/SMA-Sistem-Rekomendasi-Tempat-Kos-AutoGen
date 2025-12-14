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

if os.path.exists(nama_file):
    shutil.copy(nama_file, os.path.join(work_dir, nama_file))
    print(f"[SUCCESS] File '{nama_file}' siap digunakan.")

# --- 2. DEFINISI 5 AGEN ---

# Agen 1: UserProxy (Jembatan & Eksekutor)
user_executor = UserProxyAgent(
    name="User_Proxy",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": work_dir, "use_docker": False},
)

# Agen 2: PreferenceExtractor (Pengekstrak Kriteria)
extractor = AssistantAgent(
    name="Preference_Extractor",
    llm_config=llm_config,
    system_message="""Kamu ahli bahasa. Tugasmu mengekstrak kriteria dari teks user menjadi format: 
    - Hard: [AC/WiFi/Lokasi/Harga Max]
    - Soft: [Suasana Tenang/Dekat Kuliner/Kenyamanan]
    Hanya berikan hasil ekstraksi, jangan ada penjelasan lain."""
)

# Agen 3: KosDataAgent (Pembuat Kode Python)
data_agent = AssistantAgent(
    name="Kos_Data_Agent",
    llm_config=llm_config,
    system_message=f"""Kamu Pakar Python. Buat kode untuk filter file '{nama_file}'.
    ATURAN: 
    1. Read CSV (sep=';'). 
    2. Clean 'price' ke 'price_final' (numerik). 
    3. Filter Hard Constraint saja. 
    4. Output: Tampilkan 5 kos termurah dengan .to_string(index=False).
    Hanya berikan kode dalam blok ```python."""
)

# Agen 4: SoftPreferenceAgent (Penalar Subjektif)
soft_agent = AssistantAgent(
    name="Soft_Preference_Agent",
    llm_config=llm_config,
    system_message="""Kamu Penalar Suasana. Bandingkan tabel kos yang diberikan dengan kriteria Soft (Tenang/Nyaman).
    Gunakan logika: Nama jalan besar = ramai, Nama perumahan/gang = tenang. 
    Berikan penilaian singkat untuk setiap kos di tabel."""
)

# Agen 5: RecommendationWriter (Penulis Final)
writer = AssistantAgent(
    name="Recommendation_Writer",
    llm_config=llm_config,
    system_message="""Kamu Penulis Rekomendasi. Ringkas hasil menjadi 2-3 kos terbaik. 
    Jelaskan TRADE-OFF nya (Contoh: Lebih murah tapi jauh). 
    Gunakan bahasa yang persuasif dan ramah. Akhiri dengan TERMINATE."""
)

# --- 3. RUNNING SEQUENTIAL CHAT (5 LANGKAH) ---

print("\n" + "="*60)
print("SISTEM REKOMENDASI KOS 5-AGEN (ACADEMIC ARCHITECTURE)")
print("="*60)
user_input = input("\nMasukkan kriteria kos Anda: ")

# LANGKAH 1: Ekstraksi Kriteria
print("\n[STEP 1] Mengekstrak kriteria...")
chat_extractor = user_executor.initiate_chat(extractor, message=user_input, clear_history=True, silent=True)
kriteria = chat_extractor.last_message()["content"]

# LANGKAH 2: Filter Data (Coding)
print("[STEP 2] Memfilter data keras...")
chat_data = user_executor.initiate_chat(data_agent, message=f"Kriteria: {kriteria}", clear_history=True)
# Mengambil hasil print dari terminal
raw_table = user_executor.last_message(data_agent)["content"].split("Code output:")[1].strip()

# LANGKAH 3: Evaluasi Suasana (Soft Constraint)
print("[STEP 3] Mengevaluasi suasana & kenyamanan...")
chat_soft = user_executor.initiate_chat(soft_agent, message=f"Tabel: {raw_table}\nSoft Kriteria: {kriteria}", clear_history=True, silent=True)
evaluasi_soft = chat_soft.last_message()["content"]

# LANGKAH 4: Penulisan Rekomendasi Final & Trade-off
print("[STEP 4] Menyusun rekomendasi final...")
print("-" * 60)
user_executor.initiate_chat(writer, message=f"Data: {raw_table}\nEvaluasi: {evaluasi_soft}", clear_history=True)