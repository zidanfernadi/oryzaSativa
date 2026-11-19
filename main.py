"""main.py: titik awal program SawahKu.

Jalankan dengan perintah:  python main.py
Lalu buka di browser:      http://127.0.0.1:5000
"""
from sawah.ui import aplikasi

def main():
    # debug=True: halaman error lebih jelas dan program restart otomatis saat kode diubah
    aplikasi.run(debug=True)

if __name__ == "__main__":
    main()