"""Modul ui: tampilan web SawahKu memakai Flask (HTML + CSS).

Setiap route (alamat web) memanggil PengelolaSawah di services.py.
Tampilan HTML ada di folder templates/, gaya CSS ada di folder static/.
"""
from datetime import date

from flask import Flask, render_template, request, url_for
from flask import redirect, flash

from .services import PengelolaSawah, KUNCI_URUT
from .validasi import DAFTAR_MASA_TANAM

# (kode kolom, judul di tabel)
KOLOM_TABEL = [
    ("id", "ID"),
    ("petak", "Petak"),
    ("luas", "Luas (m2)"),
    ("musim", "Musim"),
    ("tanaman", "Tanaman"),
    ("tgl_tanam", "Tgl Tanam"),
    ("tgl_panen", "Tgl Panen"),
    ("status", "Status"),
    ("hasil_kg", "Hasil (kg)"),
    ("biaya", "Biaya (Rp)"),
    ("pendapatan", "Pendapatan (Rp)"),
    ("laba", "Laba (Rp)"),
]


def format_angka(angka):
    """Ubah angka menjadi format ribuan Indonesia, misal 1500000 -> 1.500.000."""
    return f"{angka:,.0f}".replace(",", ".")


aplikasi = Flask(__name__)
aplikasi.secret_key = "sawahku-belajar"   # dibutuhkan flash() untuk pesan
aplikasi.jinja_env.filters["angka"] = format_angka   # dipakai di HTML: {{ x|angka }}
pengelola = PengelolaSawah()   # membaca data_sawah.csv saat program mulai


def buat_link_urut(kata, musim, status, kolom_urut, turun):
    """Buat link untuk judul kolom. Klik lagi pada kolom yang sama = balik urutan."""
    link = {}
    for kode, judul in KOLOM_TABEL:
        balik = (kode == kolom_urut and not turun)
        link[kode] = url_for("beranda", cari=kata, musim=musim, status=status,
                             urut=kode, turun="1" if balik else "0")
    return link


def tampilkan_halaman(form=None):
    """Susun halaman utama: ambil data sesuai pencarian, filter, dan urutan."""
    kata = request.args.get("cari", "")
    musim = request.args.get("musim", "")
    status = request.args.get("status", "")
    kolom_urut = request.args.get("urut", "id")
    turun = request.args.get("turun", "0") == "1"
    if kolom_urut not in KUNCI_URUT:
        kolom_urut = "id"

    # Kumpulkan filter yang dipilih (dikirim sebagai **kwargs)
    filter_nilai = {}
    if musim != "":
        filter_nilai["musim"] = musim
    if status != "":
        filter_nilai["status"] = status

    daftar = pengelola.ambil_tampilan(kata=kata, kolom_urut=kolom_urut,
                                      turun=turun, **filter_nilai)

    peringatan = ""
    if pengelola.jumlah_rusak > 0:
        peringatan = f"{pengelola.jumlah_rusak} baris di file data rusak dan dilewati."

    konteks = {
        "daftar": daftar,
        "total": pengelola.hitung_total(daftar),
        "kolom_tabel": KOLOM_TABEL,
        "peringatan": peringatan,
        "kata": kata,
        "musim": musim,
        "status": status,
        "kolom_urut": kolom_urut,
        "turun": turun,
        "daftar_musim": pengelola.daftar_musim(),
        "link_urut": buat_link_urut(kata, musim, status, kolom_urut, turun),
    }

    # Isian form tambah: nilai awal, atau nilai yang tadi diketik jika input salah
    isian = {
        "petak": "", "luas": "", "tahun": str(date.today().year),
        "masa_tanam": DAFTAR_MASA_TANAM[0], "tanaman": "Padi",
        "tgl_tanam": str(date.today()), "biaya": "0",
    }
    if form is not None:
        isian.update(form.to_dict())

    konteks["isian"] = isian
    konteks["daftar_masa_tanam"] = DAFTAR_MASA_TANAM
    konteks["ringkasan"] = pengelola.ringkasan_per_musim()
    konteks["hari_ini"] = str(date.today())

    return render_template("index.html", **konteks)


@aplikasi.route("/")
def beranda():
    """Halaman utama: tabel catatan."""
    return tampilkan_halaman()


def jalankan_aksi(aksi, pesan_sukses, *argumen, **opsi):
    """Jalankan satu aksi data, lalu siapkan pesan sukses atau pesan error.

    Return True jika berhasil, False jika input ditolak (ValueError).
    """
    try:
        aksi(*argumen, **opsi)
    except ValueError as pesan_error:
        flash(str(pesan_error), "error")
        return False
    flash(pesan_sukses, "sukses")
    return True


@aplikasi.route("/tambah", methods=["POST"])
def tambah():
    """Form Tambah: simpan catatan tanam baru."""
    berhasil = jalankan_aksi(
        pengelola.tambah_catatan, "Catatan berhasil ditambahkan",
        petak=request.form.get("petak", ""),
        luas=request.form.get("luas", ""),
        tahun=request.form.get("tahun", ""),
        masa_tanam=request.form.get("masa_tanam", ""),
        tanaman=request.form.get("tanaman", ""),
        tgl_tanam=request.form.get("tgl_tanam", ""),
        biaya=request.form.get("biaya", ""))

    if not berhasil:
        return tampilkan_halaman(form=request.form)   # isian tidak hilang
    return redirect(url_for("beranda"))


@aplikasi.route("/panen/<int:id_catatan>", methods=["POST"])
def panen(id_catatan):
    """Form Panen: isi tanggal panen, hasil (kg), dan pendapatan (Rp)."""
    jalankan_aksi(
        pengelola.tandai_panen, "Panen berhasil dicatat", id_catatan,
        request.form.get("tgl_panen", ""),
        request.form.get("hasil_kg", ""),
        request.form.get("pendapatan", ""))
    return redirect(url_for("beranda"))


@aplikasi.route("/biaya/<int:id_catatan>", methods=["POST"])
def biaya(id_catatan):
    """Form Biaya: tambah pengeluaran (pupuk, bibit, upah, dll)."""
    jalankan_aksi(pengelola.tambah_biaya, "Biaya berhasil ditambahkan",
                  id_catatan, request.form.get("jumlah", ""))
    return redirect(url_for("beranda"))


@aplikasi.route("/hapus/<int:id_catatan>", methods=["POST"])
def hapus(id_catatan):
    """Tombol Hapus: hapus satu catatan."""
    jalankan_aksi(pengelola.hapus_catatan, "Catatan dihapus", id_catatan)
    return redirect(url_for("beranda"))
