import json
import re
from typing import List
from pydantic import BaseModel, Field
from llm import tanya_gemini


class CodeFile(BaseModel):
    path: str = Field(description="Path file relatif, misal backend/app.py atau frontend/index.html")
    content: str = Field(description="Isi lengkap dari file")


class AgentCodeResponse(BaseModel):
    catatan: str = Field(description="Ringkasan singkat apa yang dikerjakan")
    files: List[CodeFile] = Field(description="Daftar file yang dibuat atau diubah")


class QAResponse(BaseModel):
    lulus: bool = Field(description="True jika kode lulus pengujian, False jika ada bug")
    temuan: List[str] = Field(description="Daftar bug atau masalah yang ditemukan. Kosong jika lulus.")


INSTRUKSI = {
    "UI/UX Designer": """Kamu UI/UX Designer. Tulis spesifikasi desain dalam Markdown:
daftar halaman, alur pengguna, komponen per halaman, palet warna, dan tipografi.
Jangan menulis kode.""",

    "Backend Developer": """Kamu Backend Developer. Gunakan Python Flask dan SQLite kecuali PRD
menentukan lain. Taruh semua file di folder "backend/". Tulis kode lengkap yang bisa dijalankan.""",

    "Web Developer": """Kamu Web Developer front-end. Gunakan HTML, CSS, dan JavaScript biasa
(tanpa framework) kecuali PRD menentukan lain. Taruh file di folder "frontend/".
Ikuti spesifikasi desain dan panggil API backend yang sudah dibuat. Tulis kode lengkap yang bisa dijalankan.""",

    "Mobile Developer": """Kamu Mobile Developer. Gunakan Flutter kecuali PRD menentukan lain.
Taruh file di folder "mobile/". Tulis kode lengkap yang bisa dijalankan.""",

    "Full-Stack Developer": """Kamu Full-Stack Developer. Tugasmu memperbaiki bug pada kode
yang sudah ada berdasarkan temuan QA.
PENTING:
- Kembalikan HANYA file yang benar-benar kamu ubah untuk memperbaiki bug (misal: jika bug hanya di backend/app.py dan frontend/app.js, kembalikan HANYA kedua file itu).
- JANGAN sertakan file yang tidak berubah.
- Tulis isi file yang diperbaiki secara lengkap.""",

    "QA Tester": """Kamu QA Tester. Kamu tidak bisa menjalankan kode, jadi lakukan code review ketat:
1. Apakah setiap fitur di PRD sudah ada?
2. Apakah ada bug yang jelas (error sintaks, variabel salah, import hilang)?
3. Apakah endpoint yang dipanggil frontend benar-benar ada di backend?
Bila lulus, temuan adalah list kosong. Jangan mengada-ada temuan.""",
}


def parse_json_robust(teks):
    """Parse JSON dengan toleransi tinggi jika ada markdown fences atau escape sequence tidak valid."""
    if not teks:
        raise ValueError("Respon kosong")
    
    t = teks.strip()

    # 1. Bersihkan markdown codeblock
    if "```" in t:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", t)
        if match:
            t = match.group(1).strip()
        else:
            t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.MULTILINE)
            t = re.sub(r"\s*```$", "", t, flags=re.MULTILINE)

    # 2. Cari batas kurung kurawal terluar
    awal = t.find("{")
    akhir = t.rfind("}")
    if awal != -1 and akhir != -1 and akhir > awal:
        t = t[awal:akhir + 1]

    # 3. Coba parse langsung
    try:
        return json.loads(t, strict=False)
    except Exception:
        pass

    # 4. Perbaiki escape sequence tidak valid dalam string (misal regex \d, \w, \s)
    t_fixed = re.sub(r'\\([^"\\/bfnrtu])', r'\\\\\1', t)
    try:
        return json.loads(t_fixed, strict=False)
    except Exception:
        pass

    # 5. Coba perbaiki string yang terpotong
    if t_fixed.count('"') % 2 != 0:
        t_fixed += '"'
    open_braces = t_fixed.count("{") - t_fixed.count("}")
    if open_braces > 0:
        t_fixed += "}" * open_braces
    return json.loads(t_fixed, strict=False)


def kerjakan(peran, tugas, prd, konteks="", coba_maks=3):
    """Menjalankan satu agen. Hasil: teks (UI/UX) atau dict JSON (peran lain)."""
    prompt = (
        f"PRD proyek:\n{prd}\n\n"
        f"Tugasmu: {tugas['judul']}\n{tugas['deskripsi']}\n\n"
        f"Konteks dari rekan tim:\n{konteks or '(belum ada)'}"
    )
    if peran == "UI/UX Designer":
        return tanya_gemini(prompt, instruksi_sistem=INSTRUKSI[peran])

    schema = QAResponse if peran == "QA Tester" else AgentCodeResponse

    for percobaan in range(1, coba_maks + 1):
        hasil = tanya_gemini(prompt, instruksi_sistem=INSTRUKSI[peran], schema=schema)
        try:
            return json.loads(hasil)
        except Exception:
            try:
                return parse_json_robust(hasil)
            except Exception as e:
                print(f"  ({peran} format JSON diperbaiki: {e}, mengulang {percobaan}/{coba_maks})")
    raise RuntimeError(f"{peran} gagal menghasilkan JSON yang valid.")