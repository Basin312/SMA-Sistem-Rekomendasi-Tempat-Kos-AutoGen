# SMA: Sistem Rekomendasi Tempat Kos Multi-Agen

**Sistem analisis data properti kost berbasis Multi-Agent System yang menggabungkan kemampuan kalkulasi Python dengan penalaran strategis LLM (Phi-3 Mini via Ollama).**

---

## 1. Latar Belakang (Background)

Pemilihan tempat kos adalah keputusan krusial karena menyangkut kebutuhan primer dan kenyamanan jangka panjang. Namun, proses pencarian saat ini memiliki kendala signifikan:

- **Inefisiensi Manual:** Pengguna sering menghabiskan waktu menyisir iklan media sosial yang tidak terstruktur.
- **Keterbatasan Filter Konvensional:** Sistem pencarian biasa hanya menyaring data berdasarkan angka (Harga & Jarak), namun gagal menangkap nuansa kebutuhan pengguna.

Dalam realitasnya, pengguna memiliki dua jenis kebutuhan:

1.  **Hard Constraints (Kriteria Keras):** Syarat mutlak (Cth: "Wajib WiFi", "Harga < 1 Juta").
2.  **Soft Preferences (Kriteria Lunak):** Preferensi subjektif (Cth: "Lingkungan tenang", "Vibe nyaman").

Sistem konvensional sering gagal menangani **Trade-off** (kompromi), misalnya ketika pengguna harus memilih antara "Dekat tapi Mahal" vs "Jauh tapi Fasilitas Lengkap".

### Solusi: Pendekatan Multi-Agen

Proyek ini mengembangkan **Sistem Rekomendasi Tempat Kos berbasis Multi-Agen** yang melampaui sekadar _filtering_. Sistem ini dirancang untuk:

1.  **Interpretasi Alami:** Memahami deskripsi kebutuhan pengguna dalam bahasa sehari-hari.
2.  **Smart Filtering & Reasoning:** Agen bekerja sama untuk menyaring data keras sekaligus menalar preferensi lunak.
3.  **Evaluasi Trade-off:** Memberikan rekomendasi yang "masuk akal" secara personal, bukan sekadar yang "masuk kriteria" secara matematis.

---

## 2. Arsitektur Agen dan Alur Kerja

Sistem ini dibangun menggunakan framework **PyAutogen** yang memanfaatkan model lokal **Ollama** untuk eksekusi kode yang handal.

### 2.1. Komponen Agen

| Nama Agen           | Base Model           | Peran Utama                                                                                                                                                                                                                     |
| :------------------ | :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **`kost_coder`**    | `phi3:mini` (Custom) | **Assistant Agent (Pakar Data):** Menganalisis _system message_ dan permintaan pengguna, lalu menulis kode Python yang aman dan akurat untuk _data cleaning_, _filtering_, dan _sorting_ data (`data_kos.csv`).                 |
| **`user_executor`** | N/A                  | **User Proxy Agent (Eksekutor):** Menerima input pengguna, menjalankan kode Python yang dikirim `kost_coder` di folder `coding/`, dan melaporkan hasil atau _error traceback_ kembali ke `kost_coder` untuk perbaikan otomatis. |

### 2.2. Alur Kerja (Workflow)

1.  **Inisiasi:** Pengguna memasukkan permintaan ke `user_executor` (via `main.py`).
2.  **Generasi Kode:** `kost_coder` menghasilkan kode Python berdasarkan _request_ dan **aturan wajib** dalam _system message_ (misalnya: wajib pakai delimiter `;` dan kolom `price_final`).
3.  **Eksekusi & Loop Perbaikan:** `user_executor` mengeksekusi kode di `work_dir` (`coding/`). Jika kode gagal, _traceback_ dikirim ke `kost_coder` agar agen dapat memperbaiki kodenya (**Self-Correction Loop**).
4.  **Output:** Jika kode berhasil (`exitcode: 0`), hasil rekomendasi ditampilkan kepada pengguna.

---

## 3. Instalasi & Konfigurasi

### A. Prasyarat

Pastikan sistem Anda memiliki:

- **Python 3.9+**
- **[Ollama](https://ollama.com/)** (Versi Terbaru, server harus berjalan saat program dieksekusi)
- File `requirements.txt` dan `main.py` tersedia di root repositori.

### B. Setup Lingkungan Python

**1. Buat Virtual Environment (Disarankan)**

- **Windows (PowerShell):**

  ```bash
  python -m venv venv
  .\venv\Scripts\activate
  ```

- **Mac / Linux (Bash):**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

**2. Install Dependencies**

Setelah virtual environment aktif (ditandai (venv) di terminal), jalankan:

```bash
 pip install -r requirements.txt
```

### C. Konfigurasi Model LLM (Ollama)

Kita akan membuat model kustom kost_coder dari Phi-3 Mini untuk memastikan agen berperilaku sebagai data scientist yang patuh pada instruksi.

**1. Pull Model Dasar**

Pastikan server Ollama berjalan, lalu pull model dasar yang akan dimodifikasi:

```bash
 ollama pull phi3:mini
```

**2. Buat Modelfile**
Buat file baru di root proyek Anda bernama Modelfile (tidak perlu diberi tipe) dan isi dengan konten berikut:

```Code snippet
  FROM phi3:mini

  # Agar codingan konsisten & tidak ngawur
  PARAMETER temperature 0.1

  SYSTEM """
  Kamu adalah Kost Coder, asisten pembuat kode Python.
  Tugasmu:
  1. Jika user minta load data excel/csv, panggil fungsi 'load_data' yang tersedia.
  2. Jangan minta user jalankan kode, kamu yang harus memanggil tool itu.
  3. Setelah tool sukses loading data, jelaskan isi datanya (jumlah baris/kolom) lalu balas TERMINATE.
  """
```

**3. Buat Model Kustom**

Gunakan perintah create Ollama untuk membuat model yang akan digunakan oleh main.py:

```bash
 ollama create kost_coder -f ./Modelfile
```

## 4. Cara Menjalankan Aplikasi

### A. Persiapan Data

**1. Pastikan file data bernama data_kos.csv diletakkan di root folder proyek.**
**2. Opsional: Pindahkan file data_kos.csv secara manual ke dalam folder coding/ untuk menghindari potensi FileNotFoundError saat eksekusi.**

### B. Eksekusi Script Utama

Jalankan main.py dari terminal Anda (pastikan (venv) aktif):

```bash
 python main.py
```

### C. Interaksi

Sistem akan meminta Anda memasukkan kriteria pencarian. Agen akan secara otomatis menulis, menjalankan, dan menampilkan hasil rekomendasinya.

Contoh Permintaan:

```
=======================================================
SISTEM PENCARI KOS (FINAL FIX)
=======================================================

Masukkan pencarian (cth: kos murah ada wifi atau kos di Depok AC max 2 juta): carikan top 5 kos di Jakarta Selatan ada WiFi
```
