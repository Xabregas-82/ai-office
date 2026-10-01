# 🏢 AI Virtual Office

AI Virtual Office adalah platform simulasi kantor perangkat lunak virtual berbasis Multi-Agent System yang ditenagai oleh Google Gemini API. Sistem ini mengotomatiskan seluruh alur pengembangan software: mulai dari analisis PRD, perencanaan tugas, desain UI/UX, penulisan kode (frontend, backend, mobile), hingga quality assurance (QA review & bug fixing).

Dilengkapi dengan antarmuka 3D visual interaktif dan real-time status update melalui WebSocket.

---

## 🌟 Fitur Utama

- **🧠 Multi-Agent Collaboration**:
  - **Product Manager (PM)**: Membaca PRD, memecah fitur menjadi daftar tugas modular dan dependensinya.
  - **UI/UX Designer**: Membuat arsitektur informasi, alur pengguna, skema warna, dan wireframe konsep.
  - **Backend Developer**: Menulis API dan database (Flask, SQLite, dll.).
  - **Web / Frontend Developer**: Mengembangkan antarmuka web responsif (HTML/CSS/JS).
  - **Mobile Developer**: Menulis aplikasi mobile (Flutter).
  - **QA Tester**: Melakukan code review ketat terhadap PRD & kode sumber, mendeteksi bug, dan memberikan laporan temuan.
  - **Full-Stack Developer**: Menerima temuan QA dan otomatis memperbaiki bug hingga lulus uji.
- **🌐 Real-Time 3D Office Visualization**:
  - Visualisasi 3D kantor virtual menggunakan Three.js di browser.
  - Live status & balon obrolan agen saat sedang merencanakan, mendesain, mengoding, maupun review.
- **⚡ FastAPI & WebSocket**:
  - Komunikasi backend-frontend instan dan responsif.
  - REST endpoint untuk pemicuan simulasi dan monitoring progress.

---

## 📁 Struktur Direktori

```text
ai-office/
├── agents.py           # Definisi prompt, peran agen, dan parser respons
├── llm.py              # Integrasi Google Gemini API
├── office.py           # Orkestrasi alur kerja antar-agen (workflow)
├── pm_agent.py         # Logika PM untuk dekomposisi PRD menjadi tugas
├── server.py           # FastAPI backend server & WebSocket hub
├── prd/                # Folder penyimpanan dokumen PRD (Markdown)
│   ├── contoh_prd.md
│   └── current.md
├── output/             # Output hasil kerja agen AI
│   ├── desain/         # Output spesifikasi UI/UX
│   └── proyek/         # Kode program yang dihasilkan agen
├── web/
│   └── index.html      # Antarmuka frontend 3D & kontrol panel
├── .env.example        # Contoh konfigurasi variabel lingkungan
├── requirements.txt    # Daftar dependensi Python
└── README.md           # Dokumentasi proyek
```

---

## 🚀 Panduan Memulai

### 1. Clone Repository
```bash
git clone https://github.com/RizkiNurmahmudi/ai-office.git
cd ai-office
```

### 2. Buat & Aktifkan Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependensi
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Variabel Lingkungan
Salin file `.env.example` menjadi `.env` dan masukkan API Key Google Gemini Anda:
```bash
cp .env.example .env
```

Isi di dalam `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

---

## 💻 Menjalankan Aplikasi

Jalankan server FastAPI:
```bash
python server.py
```

Buka browser dan akses:
```
http://localhost:8000
```

1. Masukkan spesifikasi PRD atau pilih contoh PRD yang tersedia.
2. Klik tombol untuk memulai simulasi kantor virtual.
3. Pantau agen-agen bekerja secara visual di kantor 3D secara real-time!
4. Hasil kode program akan otomatis disimpan di folder `output/proyek/`.

---

## 📄 Lisensi

Distributed under the MIT License. See `LICENSE` for more information.
