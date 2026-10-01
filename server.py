"""
server.py — FastAPI server untuk AI Virtual Office.
Menghubungkan backend AI (Gemini agents) dengan frontend 3D via WebSocket.

Jalankan:  python server.py
Buka:      http://localhost:8000
"""

import asyncio
import json
import os
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from starlette.requests import Request

# ── State ──
clients: set = set()
event_loop = None
sedang_berjalan = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_loop
    event_loop = asyncio.get_running_loop()
    yield


app = FastAPI(title="AI Virtual Office", lifespan=lifespan)


# ── WebSocket ──
@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()  # keep-alive
    except Exception:
        pass
    finally:
        clients.discard(ws)


async def _kirim_ke_semua(data: str):
    mati = set()
    for ws in list(clients):
        try:
            await ws.send_text(data)
        except Exception:
            mati.add(ws)
    for m in mati:
        clients.discard(m)


def lapor(agen: str, status: str, pesan: str = ""):
    """Callback untuk office.py — kirim status ke semua client WebSocket + print ke terminal."""
    print(f"  [{agen}] {status}: {pesan}")
    data = json.dumps({"agent": agen, "status": status, "pesan": pesan}, ensure_ascii=False)
    if event_loop and not event_loop.is_closed():
        asyncio.run_coroutine_threadsafe(_kirim_ke_semua(data), event_loop)


# ── API ──
@app.get("/api/contoh-prd")
async def get_contoh_prd():
    try:
        if os.path.exists("prd/contoh_prd.md"):
            with open("prd/contoh_prd.md", "r", encoding="utf-8") as f:
                return {"prd": f.read()}
    except Exception as e:
        pass
    return {"prd": "# PRD: Todo App\n\n## Fitur\n1. Tambah todo\n2. Hapus todo\n3. Checklist selesai"}


@app.get("/api/download")
async def download_output():
    import io
    import zipfile
    from starlette.responses import StreamingResponse

    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        if os.path.exists("output"):
            for root, dirs, files in os.walk("output"):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, "output")
                    zf.write(full_path, arcname=rel_path)
    mem.seek(0)
    return StreamingResponse(
        mem,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="ai-office-output.zip"'}
    )


@app.get("/api/output-files")
async def list_output_files():
    hasil = []
    if os.path.exists("output"):
        for root, dirs, files in os.walk("output"):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, "output").replace("\\", "/")
                size = os.path.getsize(full_path)
                hasil.append({"path": rel_path, "size": size})
    return {"files": hasil}


@app.get("/api/file-content")
async def get_file_content(path: str):
    base = os.path.abspath("output")
    target = os.path.abspath(os.path.join(base, path))
    if not target.startswith(base) or not os.path.exists(target) or os.path.isdir(target):
        return JSONResponse({"error": "File tidak ditemukan"}, status_code=404)
    try:
        with open(target, "r", encoding="utf-8", errors="replace") as f:
            return {"content": f.read()}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/mulai")
async def mulai_proyek(request: Request):
    global sedang_berjalan
    if sedang_berjalan:
        return JSONResponse({"error": "Proyek sedang berjalan, tunggu hingga selesai."}, status_code=409)

    body = await request.json()
    teks_prd = body.get("prd", "").strip()
    if not teks_prd:
        return JSONResponse({"error": "PRD kosong."}, status_code=400)

    sedang_berjalan = True
    t = threading.Thread(target=_jalankan_proyek, args=(teks_prd,), daemon=True)
    t.start()
    return {"status": "started"}


def _jalankan_proyek(prd_text: str):
    global sedang_berjalan
    try:
        from pm_agent import jalankan_pm
        from office import jalankan_kantor

        # Simpan PRD
        os.makedirs("prd", exist_ok=True)
        with open("prd/current.md", "w", encoding="utf-8") as f:
            f.write(prd_text)

        # 1. PM membaca PRD dan membuat rencana
        lapor("Project Manager", "working", "Membaca PRD...")
        rencana = jalankan_pm(prd_text)
        ringkasan = rencana.get("ringkasan", "Rencana siap")
        jumlah = len(rencana.get("tugas", []))
        lapor("Project Manager", "done", f"{ringkasan} ({jumlah} tugas)")

        # Simpan rencana
        os.makedirs("output", exist_ok=True)
        with open("output/tugas.json", "w", encoding="utf-8") as f:
            json.dump(rencana, f, ensure_ascii=False, indent=2)

        # 2. Jalankan seluruh tim
        jalankan_kantor(rencana, prd_text, lapor=lapor)

        # 3. Selesai
        lapor("System", "done", "Proyek selesai! Cek folder output/")

    except Exception as e:
        lapor("System", "found_bugs", f"Error: {str(e)[:100]}")
        import traceback
        traceback.print_exc()
    finally:
        sedang_berjalan = False


# ── Serve frontend (HARUS paling bawah) ──
app.mount("/", StaticFiles(directory="web", html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("  AI Virtual Office Server")
    print("  Buka: http://localhost:8000")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
