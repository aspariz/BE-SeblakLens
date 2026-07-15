from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import tempfile
import base64
import json
from dotenv import load_dotenv

# 1. Mengambil kunci rahasia dari file .env
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

# 2. Mengaktifkan server Flask
app = Flask(__name__)
CORS(app)

# 3. Memilih otak Gemini
model = genai.GenerativeModel('gemini-1.5-flash')

# 4. Daftar Harga Toping (Semua kunci diubah menjadi huruf kecil agar aman)
HARGA = {
    "jamur enoki": 2000, "fishroll": 2500, "dumpling ayam": 3000,
    "cuanki": 1500, "chikuwa long": 2500, "batagor": 2000,
    "bakso": 2000, "kerupuk": 1000, "telor": 2000, "sosis": 2000, 
    "kwetiau": 3000, "mie": 2000, "tahu": 1500, "macaroni": 2000, "sayur": 1500
}

# 5. Jalur utama untuk menerima gambar dari web
@app.route('/hitung-seblak', methods=['POST'])
def hitung():
    data = request.json
    
    if not data or 'gambar' not in data:
        return jsonify({"status": "error", "pesan": "Data gambar tidak ditemukan"}), 400
        
    try:
        gambar_b64 = data['gambar'].split(",")[1]
        gambar_bytes = base64.b64decode(gambar_b64)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(gambar_bytes)
            temp_path = temp_file.name
            
        sample_file = genai.upload_file(path=temp_path)
        
        # PROMPT: Titipan pesan untuk Gemini
        prompt = """
        Kamu adalah sistem AI Computer Vision tingkat lanjut yang bertugas sebagai kasir otomatis di warung seblak.
        Tugas mutlakmu adalah memindai gambar mangkuk seblak ini dan menghitung jumlah toping secara visual dengan tingkat akurasi 100%.

        ATURAN ANALISIS VISUAL (WAJIB DIIKUTI):
        1. Pindai gambar dengan sangat teliti dari berbagai sudut. Perhatikan toping yang mungkin saling bertumpuk, terpotong, atau sebagian terendam kuah.
        2. ANTI-HALUSINASI: Jangan pernah menebak-nebak. Hanya hitung objek yang benar-benar terlihat jelas oleh matamu. Jika ragu, jangan dihitung.
        3. Bedakan bentuk dengan cermat (misal: sosis vs chikuwa long, mie vs kwetiau, batagor vs cuanki).

        ATURAN PENAMAAN TOPING:
        Kamu HANYA diizinkan menggunakan nama toping dari daftar ini, dan tulisan HANYA boleh menggunakan huruf kecil persis seperti ini:
        "jamur enoki", "fishroll", "dumpling ayam", "cuanki", "chikuwa long", "batagor", "bakso", "kerupuk", "telor", "sosis", "kwetiau", "mie", "tahu", "macaroni", "sayur".

        ATURAN OUTPUT (SANGAT KRUSIAL):
        Sistem backend saya akan hancur jika kamu memberikan teks selain JSON. 
        Oleh karena itu, kembalikan jawaban HANYA berupa array JSON murni. Dilarang keras menambahkan kalimat sapaan, penjelasan, atau format markdown seperti ```json atau ```.
        
        Contoh format balasan yang benar:
        [
          {"nama": "bakso", "jumlah": 3},
          {"nama": "telor", "jumlah": 1},
          {"nama": "kerupuk", "jumlah": 5}
        ]
        
        Jika tidak ada toping seblak yang dikenali dalam gambar, kembalikan array kosong persis seperti ini:
        []
        """
        
        response = model.generate_content([sample_file, prompt])
        
        # Bersihkan markdown jika Gemini tidak sengaja menyertakannya
        hasil_teks = response.text.replace('```json', '').replace('```', '').strip()
        data_toping = json.loads(hasil_teks)
        
        keranjang = []
        total_harga = 0
        
        # 6. Menghitung harga total
        for item in data_toping:
            nama = item['nama'].lower().strip()
            jumlah = item['jumlah']
            
            if jumlah > 0:
                harga_satuan = HARGA.get(nama, 0)
                subtotal = harga_satuan * jumlah
                total_harga += subtotal
                
                keranjang.append({
                    "nama": nama,
                    "jumlah": jumlah,
                    "subtotal": subtotal
                })

        # Mengembalikan struk ke web
        return jsonify({
            "status": "sukses",
            "keranjang": keranjang,
            "total_harga": total_harga
        })

    except Exception as e:
        return jsonify({"status": "error", "pesan": str(e)}), 500
    finally:
        # Memastikan file temporary terhapus dari server agar storage tidak penuh
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.remove(temp_path)

# 7. Menyalakan Server (Sudah dibersihkan dari kode duplikat)
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port)