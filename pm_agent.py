import json
import os
from typing import List
from pydantic import BaseModel, Field
from llm import tanya_gemini

class TugasItem(BaseModel):
    id: str = Field(description="ID tugas unik, misal T1, T2")
    judul: str = Field(description="Judul singkat tugas")
    deskripsi: str = Field(description="Apa yang harus dikerjakan secara spesifik")
    peran: str = Field(description="Salah satu: UI/UX Designer, Backend Developer, Web Developer, Mobile Developer, QA Tester")
    bergantung_pada: List[str] = Field(description="List ID tugas lain yang harus selesai dulu, kosong jika tidak ada")
    prioritas: str = Field(description="tinggi | sedang | rendah")

class PMResponse(BaseModel):
    ringkasan: str = Field(description="Ringkasan proyek 1-2 kalimat")
    tugas: List[TugasItem] = Field(description="Daftar tugas terstruktur")

INSTRUKSI_PM = """
Kamu adalah Project Manager berpengalaman di tim pengembangan aplikasi mobile dan website.
Tugasmu: membaca PRD lalu memecahnya menjadi tiket tugas yang jelas dan berurutan.

Peran yang tersedia di tim: "UI/UX Designer", "Backend Developer", "Web Developer", "Mobile Developer", "QA Tester".

Aturan:
- Tiap tugas harus kecil, spesifik, dan bisa dikerjakan satu orang.
- Tentukan ketergantungan antar tugas (misalnya desain dulu sebelum coding).
- Tugas QA Tester selalu ada di akhir.
"""


def jalankan_pm(teks_prd):
    prompt = f"Berikut PRD-nya:\n\n{teks_prd}\n\nPecah menjadi tiket tugas."
    hasil = tanya_gemini(prompt, instruksi_sistem=INSTRUKSI_PM, schema=PMResponse)
    return json.loads(hasil)


if __name__ == "__main__":
    with open("prd/contoh_prd.md", encoding="utf-8") as f:
        prd = f.read()

    print("PM sedang membaca PRD...\n")
    rencana = jalankan_pm(prd)

    print("Ringkasan:", rencana["ringkasan"], "\n")
    for t in rencana["tugas"]:
        print(f'{t["id"]} [{t["peran"]}] {t["judul"]}  (setelah: {t["bergantung_pada"]})')

    os.makedirs("output", exist_ok=True)
    with open("output/tugas.json", "w", encoding="utf-8") as f:
        json.dump(rencana, f, ensure_ascii=False, indent=2)
    print("\nDaftar tugas disimpan di output/tugas.json")