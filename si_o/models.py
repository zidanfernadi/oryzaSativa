"""Modul models: berisi class Catatan.

Satu objek Catatan = satu catatan musim tanam untuk satu petak sawah.
Contoh: Petak Utara, musim 2026-MT1, ditanami Padi, hasil 1600 kg.
"""

# Jumlah kolom yang harus ada di setiap baris file CSV
JUMLAH_KOLOM = 11


class Catatan:
    """Menyimpan data satu musim tanam di satu petak."""

    def __init__(self, id_catatan, petak, luas, musim, tanaman, tgl_tanam,
                 tgl_panen="-", status="Tanam", hasil_kg=0.0,
                 biaya=0.0, pendapatan=0.0):
        self.id_catatan = id_catatan    # nomor unik catatan
        self.petak = petak              # nama petak, misal "Petak Utara"
        self.luas = luas                # luas petak (meter persegi)
        self.musim = musim              # misal "2026-MT1"
        self.tanaman = tanaman          # misal "Padi"
        self.tgl_tanam = tgl_tanam      # format YYYY-MM-DD
        self.tgl_panen = tgl_panen      # "-" jika belum panen
        self.status = status            # "Tanam" atau "Panen"
        self.hasil_kg = hasil_kg        # hasil panen (kg)
        self.biaya = biaya              # total biaya (Rp)
        self.pendapatan = pendapatan    # pendapatan dari hasil panen (Rp)

    def hitung_laba(self):
        """Laba = pendapatan dikurangi biaya."""
        return self.pendapatan - self.biaya

    def ke_baris(self):
        """Ubah objek menjadi satu baris teks (dipisah koma) untuk file."""
        kolom = [
            str(self.id_catatan), self.petak, str(self.luas), self.musim,
            self.tanaman, self.tgl_tanam, self.tgl_panen, self.status,
            str(self.hasil_kg), str(self.biaya), str(self.pendapatan),
        ]
        return ",".join(kolom)


def dari_baris(baris):
    """Ubah satu baris teks dari file menjadi objek Catatan.

    Raise ValueError jika jumlah kolom salah atau angka tidak valid
    (artinya baris file rusak).
    """
    kolom = baris.strip().split(",")
    if len(kolom) != JUMLAH_KOLOM:
        raise ValueError(f"Jumlah kolom harus {JUMLAH_KOLOM}, ditemukan {len(kolom)}")

    return Catatan(
        id_catatan=int(kolom[0]),
        petak=kolom[1],
        luas=float(kolom[2]),
        musim=kolom[3],
        tanaman=kolom[4],
        tgl_tanam=kolom[5],
        tgl_panen=kolom[6],
        status=kolom[7],
        hasil_kg=float(kolom[8]),
        biaya=float(kolom[9]),
        pendapatan=float(kolom[10]),
    )