import urllib.parse


def generate_name_dorks(full_name: str) -> dict:
    cleaned = full_name.strip().strip('"').strip("'")
    if not cleaned:
        return {"success": False, "error": "Nama tidak boleh kosong."}

    catalog = {
        "Dokumen Pribadi, CV & Resume": [
            {
                "title": "Dokumen CV / Resume PDF",
                "query": f'"{cleaned}" ("curriculum vitae" OR "resume" OR "CV") filetype:pdf',
                "desc": "Mencari berkas PDF CV, biodata lamaran kerja, atau riwayat hidup."
            },
            {
                "title": "Portofolio / Proposal Pribadi",
                "query": f'"{cleaned}" (inurl:portfolio OR inurl:resume OR inurl:cv) (filetype:pdf OR filetype:doc)',
                "desc": "Mencari berkas portofolio atau proposal proyek yang pernah diunggah."
            }
        ],
        "Pendidikan & Rekam Akademis": [
            {
                "title": "PDDikti & Kampus Indonesia",
                "query": f'"{cleaned}" (site:pddikti.kemdikbud.go.id OR site:ac.id OR site:edu)',
                "desc": "Mencari status mahasiswa/dosen resmi, universitas, dan program studi."
            },
            {
                "title": "Publikasi Ilmiah & Skripsi",
                "query": f'"{cleaned}" (site:scholar.google.com OR "skripsi" OR "thesis" OR "disertasi" OR "jurnal")',
                "desc": "Mencari karya tulis ilmiah, skripsi sarjana, atau sitasi riset."
            }
        ],
        "Profil Profesional & Karir": [
            {
                "title": "Profil Resmi LinkedIn",
                "query": f'site:linkedin.com/in/ "{cleaned}"',
                "desc": "Mencari akun profesional LinkedIn, riwayat pekerjaan, dan perusahaan saat ini."
            },
            {
                "title": "Portal Karir (Glints / JobStreet)",
                "query": f'"{cleaned}" (site:glints.com OR site:jobstreet.co.id OR site:kalibrr.com)',
                "desc": "Mencari jejak pendaftaran di portal rekrutmen dan bursa kerja."
            },
            {
                "title": "Afiliasi Bisnis / Jabatan Perusahaan",
                "query": f'"{cleaned}" ("Direktur" OR "Komisaris" OR "Manager" OR "Founder" OR "CEO")',
                "desc": "Mencari status kepemilikan bisnis, akta perseroan, atau posisi manajerial."
            }
        ],
        "Putusan Hukum & Berita Resmi Pemerintah": [
            {
                "title": "Putusan Pengadilan (Mahkamah Agung)",
                "query": f'"{cleaned}" (site:putusan3.mahkamahagung.go.id OR site:mahkamahagung.go.id)',
                "desc": "Mengecek riwayat perkara perdata/pidana atau putusan hukum resmi."
            },
            {
                "title": "JDIH & Surat Keputusan Pemerintah",
                "query": f'"{cleaned}" (site:jdih.*.go.id OR site:kemenkumham.go.id OR "Surat Keputusan")',
                "desc": "Mencari nama dalam lembaran pengumuman dinas, SK pengangkatan, atau tender."
            }
        ],
        "Jejak Media Sosial & Berita": [
            {
                "title": "Jejak Media Sosial Populer",
                "query": f'"{cleaned}" (site:facebook.com OR site:instagram.com OR site:x.com OR site:tiktok.com)',
                "desc": "Mencari postingan publik, tag foto, atau akun yang memuat nama lengkap target."
            },
            {
                "title": "Liputan Berita Media Nasional",
                "query": f'"{cleaned}" (site:detik.com OR site:kompas.com OR site:tribunnews.com OR site:kumparan.com)',
                "desc": "Mencari apakah nama target pernah menjadi narasumber atau subjek pemberitaan."
            }
        ]
    }

    results = {}
    total = 0

    for cat, items in catalog.items():
        results[cat] = []
        for it in items:
            total += 1
            encoded = urllib.parse.quote(it["query"])
            url = f"https://www.google.com/search?q={encoded}"
            results[cat].append({
                "title": it["title"],
                "query": it["query"],
                "url": url,
                "desc": it["desc"]
            })

    return {
        "success": True,
        "name": cleaned,
        "total_queries": total,
        "categories": results
    }
