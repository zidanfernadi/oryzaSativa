"""Modul services: logika pengolahan data (tanpa tampilan).

Berisi function *args, **kwargs, lambda, algoritma searching & sorting,
dan class PengelolaSawah yang mengatur seluruh data catatan.
"""
from . import storage, validasi
from .models import Catatan


# ---------------------------------------------------------------
# FUNCTION LANJUTAN
# ---------------------------------------------------------------
def jumlahkan(*angka):
    """Menjumlahkan angka sebanyak apa pun (memakai *args)."""
    total = 0
    for nilai in angka:
        total += nilai
    return total


# Kamus berisi lambda: cara mengambil nilai kolom untuk keperluan sorting
KUNCI_URUT = {
    "id": lambda catatan: catatan.id_catatan,
    "petak": lambda catatan: catatan.petak.lower(),
    "luas": lambda catatan: catatan.luas,
    "musim": lambda catatan: catatan.musim,
    "tanaman": lambda catatan: catatan.tanaman.lower(),
    "tgl_tanam": lambda catatan: catatan.tgl_tanam,
    "tgl_panen": lambda catatan: catatan.tgl_panen,
    "status": lambda catatan: catatan.status,
    "hasil_kg": lambda catatan: catatan.hasil_kg,
    "biaya": lambda catatan: catatan.biaya,
    "pendapatan": lambda catatan: catatan.pendapatan,
    "laba": lambda catatan: catatan.hitung_laba(),
}


# ---------------------------------------------------------------
# ALGORITMA SEARCHING
# ---------------------------------------------------------------
def linear_search_kata(data, kata):
    """Linear Search: periksa catatan satu per satu dari awal sampai akhir.

    Catatan dianggap cocok jika kata kunci ada di ID, nama petak,
    tanaman, atau musim.
    """
    kata = kata.lower().strip()
    hasil = []
    for catatan in data:
        teks = f"{catatan.id_catatan} {catatan.petak} {catatan.tanaman} {catatan.musim}"
        if kata in teks.lower():
            hasil.append(catatan)
    return hasil


def binary_search_id(data, id_dicari):
    """Binary Search: cari catatan berdasarkan ID.

    Syarat: data sudah terurut berdasarkan ID (menaik).
    Return indeks data, atau -1 jika tidak ditemukan.
    """
    indeks_awal = 0
    indeks_akhir = len(data) - 1

    while indeks_awal <= indeks_akhir:
        indeks_tengah = (indeks_awal + indeks_akhir) // 2
        id_tengah = data[indeks_tengah].id_catatan

        if id_tengah == id_dicari:
            return indeks_tengah
        elif id_tengah < id_dicari:
            indeks_awal = indeks_tengah + 1   # cari di bagian kanan
        else:
            indeks_akhir = indeks_tengah - 1  # cari di bagian kiri

    return -1


# ---------------------------------------------------------------
# ALGORITMA SORTING
# ---------------------------------------------------------------
def harus_geser(nilai_kiri, nilai_kartu, turun):
    """Menentukan apakah nilai di kiri harus digeser ke kanan."""
    if turun:
        return nilai_kiri < nilai_kartu
    return nilai_kiri > nilai_kartu


def insertion_sort(data, kunci, turun=False):
    """Insertion Sort yang bisa dipakai untuk kolom apa pun.

    kunci : function (biasanya lambda) untuk mengambil nilai yang diurutkan
    turun : False = menaik (A-Z, kecil-besar), True = menurun
    Data asli tidak diubah, function mengembalikan salinan yang terurut.
    """
    assert callable(kunci), "kunci harus berupa function atau lambda"

    hasil = list(data)
    for i in range(1, len(hasil)):
        kartu = hasil[i]
        nilai_kartu = kunci(kartu)
        j = i - 1

        # Geser data yang posisinya salah ke kanan
        while j >= 0 and harus_geser(kunci(hasil[j]), nilai_kartu, turun):
            hasil[j + 1] = hasil[j]
            j -= 1

        hasil[j + 1] = kartu   # tempatkan pada posisi yang benar
    return hasil