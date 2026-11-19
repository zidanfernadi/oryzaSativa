"""Unit test SawahKu (memakai unittest).

Menguji pengolahan data, searching, sorting, dan file handling
tanpa menjalankan UI.  Jalankan dengan:  python test_sawah.py
"""
import os
import tempfile
import unittest

from sawah import storage
from sawah.services import (PengelolaSawah, binary_search_id, insertion_sort,
                            jumlahkan, linear_search_kata, KUNCI_URUT)

class TestPengolahanData(unittest.TestCase):
    """Menguji tambah data, validasi, panen, dan perhitungan."""

    def setUp(self):
        """Test fixture: siapkan file sementara yang bersih untuk tiap test."""
        self.folder = tempfile.TemporaryDirectory()
        self.nama_file = os.path.join(self.folder.name, "data_uji.csv")
        self.pengelola = PengelolaSawah(nama_file=self.nama_file)

    def tearDown(self):
        """Hapus folder sementara setelah test selesai."""
        self.folder.cleanup()

    def tambah_contoh(self, petak="Petak A", tahun="2026", masa="MT1", tanaman="Padi"):
        """Bantuan: tambah satu catatan contoh."""
        return self.pengelola.tambah_catatan(
            petak=petak, luas="2000", tahun=tahun, masa_tanam=masa,
            tanaman=tanaman, tgl_tanam="2026-01-10", biaya="1000000")

    def test_tambah_catatan_berhasil(self):
        catatan = self.tambah_contoh()
        self.assertEqual(catatan.id_catatan, 1)
        self.assertEqual(catatan.musim, "2026-MT1")
        self.assertEqual(len(self.pengelola.data), 1)

    def test_luas_negatif_ditolak(self):
        with self.assertRaises(ValueError):
            self.pengelola.tambah_catatan(
                petak="Petak A", luas="-5", tahun="2026", masa_tanam="MT1",
                tanaman="Padi", tgl_tanam="2026-01-10", biaya="0")

    def test_petak_kosong_ditolak(self):
        with self.assertRaises(ValueError):
            self.pengelola.tambah_catatan(
                petak="  ", luas="2000", tahun="2026", masa_tanam="MT1",
                tanaman="Padi", tgl_tanam="2026-01-10", biaya="0")

    def test_petak_sama_musim_sama_ditolak(self):
        self.tambah_contoh()
        with self.assertRaises(ValueError):
            self.tambah_contoh()

    def test_tandai_panen_dan_hitung_laba(self):
        catatan = self.tambah_contoh()
        self.pengelola.tandai_panen(catatan.id_catatan, "2026-04-20", "1500", "9000000")
        self.assertEqual(catatan.status, "Panen")
        self.assertEqual(catatan.hitung_laba(), 8000000)   # 9 juta - 1 juta

    def test_jumlahkan_args(self):
        self.assertEqual(jumlahkan(10, 20), 30)
        self.assertEqual(jumlahkan(10, 20, 30, 40), 100)
        self.assertEqual(jumlahkan(), 0)

class TestSearchSortFile(unittest.TestCase):
    """Menguji searching, sorting, filter, dan penyimpanan file."""

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.nama_file = os.path.join(self.folder.name, "data_uji.csv")
        self.pengelola = PengelolaSawah(nama_file=self.nama_file)
        for petak, luas, tahun, masa, tanaman in [
            ("Petak Utara", "3000", "2026", "MT1", "Padi"),
            ("Petak Selatan", "1000", "2026", "MT1", "Jagung"),
            ("Petak Barat", "2000", "2026", "MT2", "Padi"),
        ]:
            self.pengelola.tambah_catatan(
                petak=petak, luas=luas, tahun=tahun, masa_tanam=masa,
                tanaman=tanaman, tgl_tanam="2026-01-10", biaya="0")

    def tearDown(self):
        self.folder.cleanup()

    def test_linear_search_kata(self):
        hasil = linear_search_kata(self.pengelola.data, "jagung")
        self.assertEqual(len(hasil), 1)
        self.assertEqual(hasil[0].petak, "Petak Selatan")

    def test_binary_search_id(self):
        self.assertEqual(binary_search_id(self.pengelola.data, 3), 2)
        self.assertEqual(binary_search_id(self.pengelola.data, 99), -1)

    def test_insertion_sort_menaik_dan_menurun(self):
        menaik = insertion_sort(self.pengelola.data, KUNCI_URUT["luas"])
        self.assertEqual([c.luas for c in menaik], [1000, 2000, 3000])
        menurun = insertion_sort(self.pengelola.data, KUNCI_URUT["luas"], turun=True)
        self.assertEqual([c.luas for c in menurun], [3000, 2000, 1000])

    def test_filter_data_kwargs(self):
        hasil = self.pengelola.filter_data(musim="2026-MT1", tanaman="Padi")
        self.assertEqual(len(hasil), 1)
        self.assertEqual(hasil[0].petak, "Petak Utara")

    def test_data_tersimpan_permanen(self):
        """Data harus tetap ada saat file dibuka lagi (aplikasi ditutup/dibuka)."""
        pengelola_baru = PengelolaSawah(nama_file=self.nama_file)
        self.assertEqual(len(pengelola_baru.data), 3)

    def test_baris_rusak_dilewati(self):
        """File corrupt tidak boleh membuat program crash."""
        with open(self.nama_file, "a") as file:
            file.write("ini,baris,rusak\n")
            file.write("x,Petak Z,abc,2026-MT1,Padi,2026-01-01,-,Tanam,0,0,0\n")
        pengelola_baru = PengelolaSawah(nama_file=self.nama_file)
        self.assertEqual(len(pengelola_baru.data), 3)
        self.assertEqual(pengelola_baru.jumlah_rusak, 2)

    def test_file_hilang_dibuat_baru(self):
        nama_baru = os.path.join(self.folder.name, "belum_ada.csv")
        daftar, rusak = storage.muat_data(nama_baru)
        self.assertEqual(daftar, [])
        self.assertTrue(os.path.exists(nama_baru))

if __name__ == "__main__":
    unittest.main()