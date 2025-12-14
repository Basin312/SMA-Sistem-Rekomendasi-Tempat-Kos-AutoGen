import os
import shutil
import pandas as pd
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager

# --- CONFIG ---
config_list = [{"model": "kost_coder", "base_url": "http://localhost:11434/v1", "api_key": "ollama"}]
llm_config = {"config_list": config_list, "cache_seed": None, "temperature": 0}

# --- SETUP FILE ---
work_dir = "coding"
if not os.path.exists(work_dir): os.makedirs(work_dir)

# NAMA FILE BARU 
nama_file = "data_kos.csv" 

# Cek & Copy Otomatis path data
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
# 1. USER EXECUTOR 
user_proxy = UserProxyAgent(
    name="user_executor",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=8, # Tambah reply limit karena obrolan lebih panjang
    code_execution_config={"work_dir": work_dir, "use_docker": False},
    system_message="""
    Executor. Anda menjalankan kode Python yang disediakan oleh kost_coder. 
    Jika kode berhasil, output akan ditampilkan. Jika gagal, berikan error traceback secara lengkap.
    """
)

# 2. KOST ANALYST (Perencana Logika)
# Agen ini adalah yang menerima request pengguna pertama kali
kost_analyst = AssistantAgent(
    name="kost_analyst",
    llm_config=llm_config,
    system_message=f"""
    Kamu adalah Ahli Analisis Data. File yang digunakan: '{nama_file}'.
    Tugasmu adalah menganalisis request pengguna dan merencanakan langkah-langkah data Pandas yang diperlukan.
    Berikan instruksi KEPADA KOST_CODER untuk menulis kode.
    WAJIB sertakan langkah-langkah spesifik ini dalam instruksimu:

    1. READ FILE: Gunakan `df = pd.read_csv('{nama_file}', sep=';')`.
    2. CLEANING HARGA: WAJIB gunakan kode yang mengubah kolom 'price' menjadi numerik 'price_final'.
    3. LOGIC FILTERING: WAJIB menggunakan `df['all_facilities_bs'].str.contains` untuk fasilitas dan `.sort_values('price_final').head(N)` untuk top N termurah.
    4. OUTPUT: WAJIB menampilkan kolom room_name, region, price, all_facilities_bs menggunakan `.to_string(index=False)`.
    5. JANGAN PERNAH MENULIS KODE PYTHON, HANYA INSTRUKSI TEKS.
    """
)

# 3. KOST CODER (Pelaksana Kode)
# Tugasnya hanya menerima instruksi dari Analyst dan menerjemahkan ke Python
kost_coder = AssistantAgent(
    name="kost_coder",
    llm_config=llm_config,
    system_message="""
    Kamu adalah Pakar Python Coding.
    Tugasmu adalah MENGAMBIL instruksi dari kost_analyst dan mengubahnya menjadi satu blok kode Python yang dapat dijalankan.
    Setelah menulis kode, kirimkan KODE PYTHON tersebut kepada user_executor.
    Jangan pernah berkomentar, hanya tulis kode Python.
    """
)

# ===============================================
# --- 2. ORKESTRASI (GROUP CHAT) ---
# ===============================================

# Daftarkan semua agen ke dalam grup
groupchat = GroupChat(
    agents=[kost_analyst, kost_coder, user_proxy], 
    messages=[], 
    max_round=10
)

# Manager mengatur alur percakapan dalam grup
manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)


# --- RUNNING SEQUENCE ---
print("\n=======================================================")
print("SISTEM PENCARI KOS (TRIPLE-AGENT: Analyst -> Coder -> Executor)")
print("=======================================================")
request = input("\nMasukkan pencarian (cth: kos murah ada wifi atau kos di Depok AC max 2 juta): ")

# Obrolan dimulai oleh user_executor dan ditujukan ke manager grup
user_proxy.initiate_chat(
    manager,
    message=f"Tolong analisis dan berikan kode Python untuk request berikut: {request}"
)