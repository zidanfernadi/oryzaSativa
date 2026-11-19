"""Modul storage: membaca dan menyimpan data ke file CSV.

Semua operasi file memakai with open() sehingga file otomatis tertutup.
Mode yang dipakai:
  'x' -> membuat file baru (tidak menimpa file lama)
  'r' -> membaca seluruh data saat aplikasi dibuka
  'a' -> menambah satu baris di akhir file (saat tambah catatan)
  'w' -> menulis ulang semua data (saat ubah/hapus catatan)
"""
import os

from .models import dari_baris

# File data disimpan di folder utama proyek (satu level di atas package ini)
FOLDER_PROYEK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMA_FILE = os.path.join(FOLDER_PROYEK, "data_sawah.csv")

HEADER = ("id,petak,luas,musim,tanaman,tgl_tanam,tgl_panen,"
          "status,hasil_kg,biaya,pendapatan")


def buat_file_jika_belum_ada(nama_file=NAMA_FILE):
    """Buat file baru berisi header dengan mode 'x'."""
    try:
        with open(nama_file, "x") as file:
            file.write(HEADER + "\n")
    except FileExistsError:
        pass  # file sudah ada, data lama aman


def muat_data(nama_file=NAMA_FILE):
    """Baca semua catatan dari file dengan mode 'r'.

    Return: (daftar_catatan, jumlah_baris_rusak).
    Jika file hilang, dibuat baru. Baris yang rusak dilewati.
    """
    daftar_catatan = []
    jumlah_rusak = 0

    try:
        with open(nama_file, "r") as file:
            for nomor, baris in enumerate(file):
                if nomor == 0 or baris.strip() == "":
                    continue  # lewati header dan baris kosong
                try:
                    daftar_catatan.append(dari_baris(baris))
                except ValueError:
                    jumlah_rusak += 1  # baris corrupt, jangan bikin crash
    except FileNotFoundError:
        buat_file_jika_belum_ada(nama_file)

    return daftar_catatan, jumlah_rusak


def tambah_baris(catatan, nama_file=NAMA_FILE):
    """Tambah satu catatan di akhir file dengan mode 'a'."""
    buat_file_jika_belum_ada(nama_file)
    with open(nama_file, "a") as file:
        file.write(catatan.ke_baris() + "\n")


def simpan_semua(daftar_catatan, nama_file=NAMA_FILE):
    """Tulis ulang seluruh data dengan mode 'w' (setelah ubah/hapus)."""
    with open(nama_file, "w") as file:
        file.write(HEADER + "\n")
        for catatan in daftar_catatan:
            file.write(catatan.ke_baris() + "\n")