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


# ---------------------------------------------------------------
# CLASS PENGELOLA DATA
# ---------------------------------------------------------------
class PengelolaSawah:
    """Mengatur seluruh catatan: tambah, ubah, hapus, cari, urut, ringkasan."""

    def __init__(self, nama_file=storage.NAMA_FILE):
        self.nama_file = nama_file
        daftar_catatan, self.jumlah_rusak = storage.muat_data(nama_file)
        # Urutkan berdasarkan ID supaya Binary Search bisa dipakai
        self.data = insertion_sort(daftar_catatan, KUNCI_URUT["id"])

    def id_berikutnya(self):
        """ID baru = ID terakhir + 1 (data selalu terurut berdasarkan ID)."""
        if len(self.data) == 0:
            return 1
        return self.data[-1].id_catatan + 1

    def tambah_catatan(self, petak, luas, tahun, masa_tanam,
                       tanaman, tgl_tanam, biaya):
        """Validasi input, lalu simpan catatan musim tanam baru."""
        petak = validasi.wajib_isi(petak, "Nama petak")
        luas = validasi.angka_positif(luas, "Luas")
        musim = validasi.validasi_musim(tahun, masa_tanam)
        tanaman = validasi.wajib_isi(tanaman, "Tanaman")
        tgl_tanam = validasi.validasi_tanggal(tgl_tanam, "Tanggal tanam")
        biaya = validasi.angka_positif(biaya, "Biaya", boleh_nol=True)

        # Satu petak hanya boleh punya satu catatan per musim
        for catatan_lama in self.data:
            if catatan_lama.petak.lower() == petak.lower() and catatan_lama.musim == musim:
                raise ValueError(f"{petak} sudah punya catatan di musim {musim}")

        catatan_baru = Catatan(
            id_catatan=self.id_berikutnya(), petak=petak, luas=luas,
            musim=musim, tanaman=tanaman, tgl_tanam=tgl_tanam, biaya=biaya,
        )
        self.data.append(catatan_baru)
        storage.tambah_baris(catatan_baru, self.nama_file)  # mode 'a'
        return catatan_baru

    def cari_catatan(self, id_catatan):
        """Ambil catatan berdasarkan ID (memakai Binary Search)."""
        indeks = binary_search_id(self.data, id_catatan)
        if indeks == -1:
            raise ValueError(f"Catatan dengan ID {id_catatan} tidak ditemukan")
        return self.data[indeks]

    def tambah_biaya(self, id_catatan, jumlah):
        """Tambah biaya musim (pupuk, bibit, upah, dll)."""
        jumlah = validasi.angka_positif(jumlah, "Biaya")
        catatan = self.cari_catatan(id_catatan)
        catatan.biaya += jumlah
        storage.simpan_semua(self.data, self.nama_file)  # mode 'w'

    def tandai_panen(self, id_catatan, tgl_panen, hasil_kg, pendapatan):
        """Isi data panen: tanggal, hasil (kg), dan pendapatan (Rp)."""
        catatan = self.cari_catatan(id_catatan)
        if catatan.status == "Panen":
            raise ValueError("Catatan ini sudah ditandai panen")

        tgl_panen = validasi.validasi_tanggal(tgl_panen, "Tanggal panen")
        if tgl_panen < catatan.tgl_tanam:   # format YYYY-MM-DD bisa dibandingkan
            raise ValueError("Tanggal panen tidak boleh sebelum tanggal tanam")
        hasil_kg = validasi.angka_positif(hasil_kg, "Hasil panen")
        pendapatan = validasi.angka_positif(pendapatan, "Pendapatan", boleh_nol=True)

        catatan.tgl_panen = tgl_panen
        catatan.hasil_kg = hasil_kg
        catatan.pendapatan = pendapatan
        catatan.status = "Panen"
        storage.simpan_semua(self.data, self.nama_file)

    def hapus_catatan(self, id_catatan):
        """Hapus satu catatan (misal salah input)."""
        indeks = binary_search_id(self.data, id_catatan)
        if indeks == -1:
            raise ValueError(f"Catatan dengan ID {id_catatan} tidak ditemukan")
        del self.data[indeks]
        storage.simpan_semua(self.data, self.nama_file)

    def filter_data(self, **filter_nilai):
        """Filter data memakai **kwargs.

        Contoh: filter_data(musim="2026-MT1", status="Panen")
        Nama argumen = nama atribut Catatan (musim, status, tanaman, petak).
        """
        hasil = self.data
        for nama_atribut, nilai in filter_nilai.items():
            hasil = [c for c in hasil if getattr(c, nama_atribut) == nilai]
        return hasil

    def ambil_tampilan(self, kata="", kolom_urut="id", turun=False, **filter_nilai):
        """Data siap tampil: difilter, dicari berdasarkan kata, lalu diurutkan."""
        hasil = self.filter_data(**filter_nilai)
        if kata.strip() != "":
            hasil = linear_search_kata(hasil, kata)
        return insertion_sort(hasil, KUNCI_URUT[kolom_urut], turun=turun)

    def daftar_musim(self):
        """Daftar musim yang pernah dicatat (tanpa duplikat, terurut)."""
        return sorted(set(catatan.musim for catatan in self.data))

    def hitung_total(self, daftar_catatan):
        """Total hasil, biaya, pendapatan, dan laba dari daftar catatan."""
        return {
            "hasil_kg": jumlahkan(*[c.hasil_kg for c in daftar_catatan]),
            "biaya": jumlahkan(*[c.biaya for c in daftar_catatan]),
            "pendapatan": jumlahkan(*[c.pendapatan for c in daftar_catatan]),
            "laba": jumlahkan(*[c.hitung_laba() for c in daftar_catatan]),
        }

    def ringkasan_per_musim(self):
        """Total per musim, berguna untuk membandingkan musim ke musim."""
        ringkasan = {}
        for musim in self.daftar_musim():
            ringkasan[musim] = self.hitung_total(self.filter_data(musim=musim))
        return ringkasan
