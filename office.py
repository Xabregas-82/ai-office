import json
import os
from agents import kerjakan

FOLDER = "output/proyek"
MAKS_PERBAIKAN = 2


def cetak_status(agen, status, pesan=""):
    print(f"[{agen}] {status}: {pesan}")


def simpan_files(files):
    """Simpan file buatan AI. Path yang mencoba keluar dari folder proyek diabaikan."""
    for f in files:
        jalur = os.path.abspath(os.path.join(FOLDER, f["path"]))
        if not jalur.startswith(os.path.abspath(FOLDER)):
            print(f"  (path ditolak: {f['path']})")
            continue
        os.makedirs(os.path.dirname(jalur), exist_ok=True)
        with open(jalur, "w", encoding="utf-8") as out:
            out.write(f["content"])


def baca_semua_kode():
    bagian = []
    for akar, _, daftar in os.walk(FOLDER):
        for nama in daftar:
            jalur = os.path.join(akar, nama)
            with open(jalur, encoding="utf-8") as f:
                bagian.append(f"=== {os.path.relpath(jalur, FOLDER)} ===\n{f.read()}")
    return "\n\n".join(bagian)


def urutkan(tugas):
    """Urutkan tugas supaya tiap tugas dikerjakan setelah ketergantungannya selesai."""
    selesai, urutan, sisa = set(), [], list(tugas)
    while sisa:
        siap = [t for t in sisa if all(d in selesai for d in t["bergantung_pada"])]
        if not siap:
            raise RuntimeError("Ketergantungan tugas saling melingkar.")
        urutan.append(siap[0])
        selesai.add(siap[0]["id"])
        sisa.remove(siap[0])
    return urutan


def jalankan_qa(tugas, prd, lapor):
    for ronde in range(MAKS_PERBAIKAN + 1):
        lapor("QA Tester", "reviewing", f"ronde {ronde + 1}")
        laporan = kerjakan("QA Tester", tugas, prd, baca_semua_kode())
        if laporan["lulus"]:
            lapor("QA Tester", "done", "LULUS")
            return "LULUS"
        temuan = "\n".join(f"- {x}" for x in laporan["temuan"])
        lapor("QA Tester", "found_bugs", "\n" + temuan)
        if ronde == MAKS_PERBAIKAN:
            break
        lapor("Full-Stack Developer", "fixing", "memperbaiki temuan QA")
        perbaikan = kerjakan(
            "Full-Stack Developer",
            {
                "judul": "Perbaiki bug dari QA",
                "deskripsi": (
                    "Perbaiki semua temuan QA berikut. Kembalikan HANYA file yang kamu ubah "
                    "(dengan isi lengkap yang sudah diperbaiki). JANGAN menyertakan file yang tidak berubah."
                ),
            },
            prd,
            f"Temuan QA:\n{temuan}\n\nKode saat ini:\n{baca_semua_kode()}",
        )
        simpan_files(perbaikan.get("files", []))
        lapor("Full-Stack Developer", "done", f"Memperbaiki {len(perbaikan.get('files', []))} file")
    lapor("QA Tester", "done", "BELUM LULUS (batas perbaikan tercapai)")
    return "BELUM LULUS"


def jalankan_kantor(rencana, prd, lapor=cetak_status):
    hasil = {}
    for t in urutkan(rencana["tugas"]):
        peran = t["peran"]
        if peran == "QA Tester":
            hasil[t["id"]] = jalankan_qa(t, prd, lapor)
            continue

        lapor(peran, "working", t["judul"])
        konteks = "\n\n".join(f"Hasil {d}:\n{hasil[d]}" for d in t["bergantung_pada"])
        keluaran = kerjakan(peran, t, prd, konteks)

        if peran == "UI/UX Designer":
            os.makedirs("output/desain", exist_ok=True)
            with open(f"output/desain/{t['id']}.md", "w", encoding="utf-8") as f:
                f.write(keluaran)
            hasil[t["id"]] = keluaran
        else:
            simpan_files(keluaran["files"])
            daftar = ", ".join(f["path"] for f in keluaran["files"])
            hasil[t["id"]] = f"{keluaran['catatan']} (file: {daftar})"
        lapor(peran, "done", t["judul"])

    print("\nSelesai. Lihat hasilnya di folder output/")


if __name__ == "__main__":
    with open("output/tugas.json", encoding="utf-8") as f:
        rencana = json.load(f)
    with open("prd/contoh_prd.md", encoding="utf-8") as f:
        prd = f.read()
    jalankan_kantor(rencana, prd)