# PeopleScout v2.0 (Identity & People OSINT Toolkit)

Dedicated modular toolkit untuk penyelidikan jejak identitas digital, username footprint, profiling teknis, email/breach audit, dan verifikasi nomor telepon.

Direktori: `D:\OSINT TOOLS\people osint`

---

## Modul & Kemampuan Utama

### 1. Username Recon (`user`)
* Multi-threaded scan ke 50+ platform developer, social, forum, gaming, dan creative:
  * **Developer & Tech:** GitHub, GitLab, Bitbucket, DockerHub, Dev.to, HuggingFace, PyPI, npm, Kaggle, Hashnode, Codeforces, LeetCode, Replit.
  * **Social & Community:** Reddit, X (Twitter), Instagram, TikTok, Threads, Bluesky, Mastodon, Pinterest, Tumblr.
  * **Messaging & Link:** Telegram, Linktree, BuyMeACoffee, Keybase.
  * **Gaming:** Steam, Chess.com, Roblox.
  * **Creative & Media:** Medium, Substack, Dribbble, Behance, SoundCloud, Spotify, Flickr, Vimeo, YouTube.
* Validasi respon HTTP status dan deteksi error text bawaan platform untuk mencegah false positive.
* Opsi interaktif untuk membuka profil yang ditemukan langsung di browser default.

### 2. Deep Profile Grabber (`profile`)
* Ekstraksi metadata publik terperinci tanpa API key:
  * **GitHub:** Nama asli, bio, perusahaan/afiliasi, lokasi geografis, blog/website, email publik, jumlah public repo/gists, followers/following, tanggal pembuatan akun, dan URL avatar.
  * **Reddit:** Display name, karma post & comment, tanggal registrasi (account age), status verified email, dan status moderator.
  * **Telegram:** Nama akun, bio publik, tautan profil, dan foto profil.

### 3. Email & Breach Intelligence (`email`)
* Validasi format email RFC 5322.
* Ekstraksi profil Gravatar dan deteksi avatar MD5.
* Integrasi database kebocoran kredensial global (XposedOrNot):
  * Tingkat risiko akun (Risk Score: Low, Medium, High).
  * Status kebocoran password teks mentah (Plaintext passwords leaked: Yes/No).
  * Daftar rincian platform yang bocor, tahun insiden, dan field data pribadi yang terekspos.
  * Tautan pivot langsung ke Epieos OSINT, Hunter.io, dan Google dorks.

### 4. Phone Intelligence (`phone`)
* Standarisasi nomor telepon lokal dan internasional (E.164, National, International, RFC 3966).
* Identifikasi operator seluler Indonesia (Telkomsel, Indosat Ooredoo, XL Axiata, Smartfren, Tri) dan internasional.
* Deteksi tipe saluran: Mobile (HP), Fixed Line (Telepon Rumah), VoIP, Toll Free.
* Wilayah geografis dan zona waktu.
* Tautan pivot langsung ke WhatsApp Chat (`wa.me`), Telegram (`t.me`), Truecaller, dan Sync.me.

### 5. Real Name Correlation Dorks (`name`)
* Kompilasi 15 query Google Dork siap pakai khusus identitas perorangan:
  * **CV, Resume & Dokumen:** Portfolio PDF, dokumen Google Drive publik, biodata.
  * **Portal Akademik & Mahasiswa:** Basis data Dikti (PDDikti), repositori skripsi/tesis kampus (`ac.id`).
  * **Karier & Profesional:** LinkedIn profile, Glints, Jobstreet, profil pembicara/seminar.
  * **Catatan Sipil, Putusan & Berita:** Putusan Mahkamah Agung, lembaran hukum JDIH, artikel berita lokal.
  * **Sosial Media:** Pencarian nama lengkap terindeks di Facebook, Instagram, Twitter/X.
* Pilihan interaktif untuk membuka Google Dork target langsung di browser.

### 6. Full Identity Dossier (`full`)
* Menjalankan seluruh rantai investigasi (Username Recon + Deep Profile + Email Audit + Phone Audit + Google Dorks).
* Menghasilkan laporan dossier visual HTML tunggal (`--export-html dossier_person_<target>.html`) bertema Daytona dark UI lengkap dengan ringkasan metrik, tabel status, dan tautan pivot.

### 7. Snowflake Timestamp & Chronolocation Decoder (`snowflake`)
* Mendekode ID numerik Snowflake (Twitter/X dan Discord).
* Mengungkap waktu pembuatan akun atau postingan secara presisi hingga milidetik (format UTC dan WIB).
* Menampilkan rincian internal worker ID, process ID, dan sequence counter.
* Menghasilkan tautan investigasi otomatis ke Wayback Machine, Archive.today, dan dork historis `to:<id>`.

### 8. Image & EXIF Forensic Geolocation Grabber (`exif`)
* Mengekstrak metadata perangkat kamera (Make, Model, Lens, Date/Time).
* Mendeteksi jejak manipulasi atau perangkat lunak editing (Photoshop, Lightroom, GIMP, Canva, Snapseed).
* Mengekstrak koordinat GPS (Lintang, Bujur, Ketinggian) dan menghasilkan tautan peta langsung (Google Maps, OpenStreetMap, Google Earth, serta kalkulator sudut bayangan matahari SunCalc).
* Mendiagnosis status kompresi gambar (apakah metadata dibersihkan oleh media sosial atau dokumen asli).

### 9. Platform Immutable Identifier Pivots (`pivot`)
* Memproses ID permanen yang tidak berubah meskipun pengguna sering mengganti nama atau handle:
  * **Google Contributor / GAIA ID:** Mengekspos ulasan Google Maps, kontribusi foto, dan album publik.
  * **Instagram PK ID:** Tautan ke viewer publik pihak ketiga (Picuki, Imginn) dan pencarian riwayat username lama.
  * **Telegram Peer ID:** Tautan pencarian analitik global (TGStat, Telemetr) dan protokol pesan langsung.

### 10. Social Graph & Sock-Puppet Intersect (`intersect`)
* Menganalisis irisan lingkaran pengikut/mengikuti (Followers/Following) antara dua akun.
* Menghitung koefisien kemiripan Jaccard untuk mendeteksi apakah akun alter/samaran terhubung ke lingkaran sosial akun utama pelaku.
* Mengisolasi daftar akun mutual (teman bersama) sebagai target investigasi prioritas.

---

## Cara Penggunaan

### 1. Melalui Menu Interaktif (Klik 2x)
* Dari folder root `D:\OSINT TOOLS\`: Klik 2x file **`Jalankan_People_OSINT.bat`**.
* Dari folder toolkit: Klik 2x file **`people_scout.bat`**.

Menu terminal interaktif menampilkan 11 modul terintegrasi:
* `[01]` Full Person Intelligence Dossier
* `[02]` Cross-Platform Username Scout (50+ Platforms)
* `[03]` Email Breach & Gravatar Intelligence
* `[04]` Phone Number & Carrier Intelligence
* `[05]` Real Name Dorking Engine
* `[06]` Profile Metadata Grabber (GitHub, Reddit, Telegram)
* `[07]` Generate Full HTML Person Dossier
* `[08]` Snowflake Timestamp & Chronolocation Decoder
* `[09]` Image & EXIF Forensic Geolocation Grabber
* `[10]` Platform Immutable Identifier Pivots (Google GAIA, Instagram PK, Telegram ID)
* `[11]` Social Graph & Circle Intersect Analysis
* `[00]` Keluar

### 2. Melalui Command Line (CLI)
```cmd
cd /d "D:\OSINT TOOLS\people osint"

# Scan username di 50+ platform
python people_scout.py user torvalds

# Ekstraksi metadata akun GitHub, Reddit, dan Telegram
python people_scout.py profile torvalds

# Audit email dan riwayat kebocoran data
python people_scout.py email target@gmail.com

# Analisis nomor telepon dan operator
python people_scout.py phone 081234567890

# Hasilkan Google Dorks untuk nama orang
python people_scout.py name "Budi Santoso"

# Dekode Twitter atau Discord Snowflake ID ke milidetik pembuatan
python people_scout.py snowflake 1630000000000000000 --platform twitter

# Ekstraksi forensik EXIF, kamera, GPS pin Google Maps, dan cek software editing
python people_scout.py exif bukti_foto.jpg

# Pivot ID permanen Google GAIA, Instagram PK, atau Telegram
python people_scout.py pivot 104829104829104829104 --platform google

# Analisis irisan mutual follower antara akun alter dan akun utama
python people_scout.py intersect "alice,bob,charlie" "bob,dave,charlie" --label-a "Akun_Alter" --label-b "Akun_Asli"

# Investigasi menyeluruh + ekspor laporan dossier HTML
python people_scout.py full torvalds --export-html dossier_torvalds.html
```
