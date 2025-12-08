# SMA: Sistem Rekomendasi Tempat Kos Multi-Agen 🤖🏠

**Sistem analisis data properti kost berbasis Multi-Agent System yang menggabungkan kemampuan kalkulasi Python dengan penalaran strategis LLM (Phi-4 via Ollama).**

---

## 📖 1. Latar Belakang (Background)

Pemilihan tempat kos adalah keputusan krusial karena menyangkut kebutuhan primer dan kenyamanan jangka panjang. Namun, proses pencarian saat ini memiliki kendala signifikan:

- **Inefisiensi Manual:** Pengguna sering menghabiskan waktu menyisir iklan media sosial yang tidak terstruktur.
- **Keterbatasan Filter Konvensional:** Sistem pencarian biasa hanya menyaring data berdasarkan angka (Harga & Jarak), namun gagal menangkap nuansa kebutuhan pengguna.

Dalam realitasnya, pengguna memiliki dua jenis kebutuhan:

1.  **Hard Constraints (Kriteria Keras):** Syarat mutlak (Cth: "Wajib WiFi", "Harga < 1 Juta").
2.  **Soft Preferences (Kriteria Lunak):** Preferensi subjektif (Cth: "Lingkungan tenang", "Vibe nyaman").

Sistem konvensional sering gagal menangani **Trade-off** (kompromi), misalnya ketika pengguna harus memilih antara "Dekat tapi Mahal" vs "Jauh tapi Fasilitas Lengkap".

### 💡 Solusi: Pendekatan Multi-Agen

Proyek ini mengembangkan **Sistem Rekomendasi Tempat Kos berbasis Multi-Agen** yang melampaui sekadar _filtering_. Sistem ini dirancang untuk:

1.  **Interpretasi Alami:** Memahami deskripsi kebutuhan pengguna dalam bahasa sehari-hari.
2.  **Smart Filtering & Reasoning:** Agen bekerja sama untuk menyaring data keras sekaligus menalar preferensi lunak.
3.  **Evaluasi Trade-off:** Memberikan rekomendasi yang "masuk akal" secara personal, bukan sekadar yang "masuk kriteria" secara matematis.

---

<!-- ## 🤖 2. Arsitektur Agen

Sistem ini terdiri dari beberapa agen otonom (via Ollama Custom Models):

| Nama Agen             | Base Model | Peran Utama                                                                                                     |
| :-------------------- | :--------- | :-------------------------------------------------------------------------------------------------------------- |
| **`kost_coder`**      | Phi-4      | **Executor.** Menulis dan memperbaiki kode Python untuk cleaning data, visualisasi, dan machine learning.       |
| **`kost_consultant`** | Phi-4      | **Advisor.** Membaca output statistik dan memberikan insight bisnis, rekomendasi harga, dan analisis trade-off. |
| **`kost_manager`**    | (Opsional) | **Orchestrator.** Mengatur aliran tugas antara Coder dan Consultant.                                            |

--- -->

## 🛠️ 2. Instalasi & Konfigurasi

Ikuti langkah-langkah di bawah ini untuk menyiapkan lingkungan pengembangan (_environment_) dan mengaktifkan agen AI.

### 📋 A. Prasyarat

Pastikan sistem Anda memiliki:

- **Python 3.9+**
- **[Ollama](https://ollama.com/)** (Versi Terbaru)
- File `requirements.txt` dan folder `agents/` yang tersedia di repositori ini.

### 🐍 B. Setup Lingkungan Python

**1. Buat Virtual Environment (Disarankan)**
Agar library proyek tidak bentrok dengan sistem komputer Anda.

- **Windows:**

  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

- **Mac / Linux:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**2. Install Dependencies**
Setelah virtual environment aktif (tandanya ada `(venv)` di terminal), jalankan:

```bash
pip install -r requirements.txt
```
