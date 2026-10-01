import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = os.getenv("GEMINI_MODEL")


def tanya_gemini(prompt, instruksi_sistem=None, schema=None, json_mode=False, percobaan_maks=5):
    """Kirim prompt ke Gemini dengan dukungan Structured Outputs (Pydantic response_schema)."""
    mime = "application/json" if (schema or json_mode) else None
    config = types.GenerateContentConfig(
        system_instruction=instruksi_sistem,
        response_mime_type=mime,
        response_schema=schema if schema else None,
        max_output_tokens=8192,
    )
    for percobaan in range(1, percobaan_maks + 1):
        try:
            respon = client.models.generate_content(
                model=MODEL, contents=prompt, config=config
            )
            return respon.text
        except (errors.ServerError, errors.ClientError) as e:
            if isinstance(e, errors.ClientError) and e.code != 429:
                raise  # error lain (mis. 404) jangan diulang, langsung tampilkan
            jeda = 5 * percobaan
            print(f"Server sibuk/kuota penuh ({percobaan}/{percobaan_maks}). Coba lagi dalam {jeda} detik...")
            time.sleep(jeda)
    raise RuntimeError("Gemini masih sibuk. Coba lagi nanti.")