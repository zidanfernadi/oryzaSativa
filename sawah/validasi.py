"""Modul validasi: fungsi untuk memeriksa input pengguna.

Semua fungsi memakai raise ValueError jika input salah, supaya pesan
errornya bisa ditampilkan di UI tanpa membuat program crash.
"""
from datetime import datetime

DAFTAR_MASA_TANAM = ["MT1", "MT2", "MT3"]


def wajib_isi(teks, nama_field):
    """Pastikan teks tidak kosong. Koma diganti spasi karena CSV memakai koma."""
    teks = teks.strip().replace(",", " ")
    if teks == "":
        raise ValueError(f"{nama_field} wajib diisi")
    return teks


def angka_positif(teks, nama_field, boleh_nol=False):
    """Ubah teks menjadi float, harus positif (atau boleh nol jika boleh_nol)."""
    teks = teks.strip()
    if teks == "" and boleh_nol:
        return 0.0

    try:
        angka = float(teks.replace(",", "."))
    except ValueError:
        raise ValueError(f"{nama_field} harus berupa angka (contoh: 2500)")

    if angka < 0 or (angka == 0 and not boleh_nol):
        raise ValueError(f"{nama_field} tidak boleh nol atau negatif")
    return angka


def validasi_tanggal(teks, nama_field):
    """Pastikan tanggal berformat YYYY-MM-DD, misal 2026-11-19."""
    teks = teks.strip()
    try:
        datetime.strptime(teks, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{nama_field} harus berformat YYYY-MM-DD (contoh: 2026-11-19)")
    return teks


def validasi_musim(tahun, masa_tanam):
    """Gabungkan tahun dan masa tanam menjadi musim, misal '2026-MT1'."""
    tahun = tahun.strip()
    if len(tahun) != 4 or not tahun.isdigit():
        raise ValueError("Tahun harus 4 angka (contoh: 2026)")
    if masa_tanam not in DAFTAR_MASA_TANAM:
        raise ValueError("Masa tanam harus MT1, MT2, atau MT3")
    return f"{tahun}-{masa_tanam}"
