import os
from server import app # Mengimpor aplikasi Flask kamu

if __name__ == "__main__":
    # Mengunci port ke 7860 (port wajib di Hugging Face)
    port = int(os.environ.get("PORT", 7860))
    app.run(host="0.0.0.0", port=port)