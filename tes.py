import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")


def tanya_gemini(prompt, percobaan_maks=5):
    """Kirim prompt ke Gemini. Kalau server sibuk (503), coba lagi dengan jeda makin lama."""
    for percobaan in range(1, percobaan_maks + 1):
        try:
            respon = client.models.generate_content(model=MODEL, contents=prompt)
            return respon.text
        except errors.ServerError as e:
            jeda = 5 * percobaan  # 5, 10, 15, 20 detik...
            print(f"Server sibuk (percobaan {percobaan}/{percobaan_maks}). Coba lagi dalam {jeda} detik...")
            time.sleep(jeda)
    raise RuntimeError("Gemini masih sibuk setelah beberapa kali percobaan. Coba lagi nanti.")


print(tanya_gemini("Perkenalkan dirimu sebagai Project Manager dalam 2 kalimat."))