"""
PeopleScout v2.0 - Advanced SOCMINT & Forensic Identifier Engine
Decodes Twitter/Discord Snowflake IDs, Google GAIA IDs, Instagram PK IDs, and Social Graph Intersect.
"""

import re
import datetime
import urllib.parse


def decode_snowflake_id(snowflake_input: str | int, platform: str = "auto") -> dict:
    """
    Decodes Twitter and Discord Snowflake IDs to extract the exact millisecond
    timestamp of account or message creation, worker ID, and historical investigation links.
    """
    raw_str = str(snowflake_input).strip()
    if not raw_str.isdigit():
        return {
            "success": False,
            "error": f"ID Snowflake harus berupa deretan angka numerik, diterima: '{raw_str}'"
        }

    snowflake_id = int(raw_str)

    # Detect platform if auto
    chosen_platform = platform.lower()
    if chosen_platform == "auto":
        # Twitter snowflakes began in late 2010 (epoch 1288834974657).
        # Discord snowflakes began in 2015 (epoch 1420070400000).
        # If ID is 18-19 digits, check which epoch produces a reasonable year (2010 - present).
        ts_twitter_ms = (snowflake_id >> 22) + 1288834974657
        ts_discord_ms = (snowflake_id >> 22) + 1420070400000

        now_ms = int(datetime.datetime.now(datetime.timezone.utc).timestamp() * 1000)

        # Discord IDs have 41 bits timestamp delta since 2015
        if 1420070400000 <= ts_discord_ms <= now_ms + 86400000:
            chosen_platform = "discord"
        elif 1288834974657 <= ts_twitter_ms <= now_ms + 86400000:
            chosen_platform = "twitter"
        else:
            chosen_platform = "twitter"

    if chosen_platform == "discord":
        epoch_ms = 1420070400000
        epoch_name = "Discord Epoch (2015-01-01)"
        timestamp_ms = (snowflake_id >> 22) + epoch_ms
        internal_worker_id = (snowflake_id & 0x3E0000) >> 17
        internal_process_id = (snowflake_id & 0x1F000) >> 12
        sequence = snowflake_id & 0xFFF
    else:
        chosen_platform = "twitter"
        epoch_ms = 1288834974657
        epoch_name = "Twitter Epoch (2010-11-04)"
        timestamp_ms = (snowflake_id >> 22) + epoch_ms
        internal_worker_id = (snowflake_id >> 12) & 0x3FF
        internal_process_id = (snowflake_id >> 17) & 0x1F
        sequence = snowflake_id & 0xFFF

    # Convert to timestamps
    try:
        dt_utc = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, datetime.timezone.utc)
        # Indonesian Western Time (WIB) is UTC+7
        wib_tz = datetime.timezone(datetime.timedelta(hours=7))
        dt_wib = dt_utc.astimezone(wib_tz)

        date_str_utc = dt_utc.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " UTC"
        date_str_wib = dt_wib.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " WIB"
        iso_str = dt_utc.isoformat()
        date_only = dt_utc.strftime("%Y-%m-%d")
    except (ValueError, OverflowError, OSError) as err:
        return {
            "success": False,
            "error": f"Kalkulasi waktu gagal dari ID {snowflake_id}: {err}"
        }

    # Investigation & Archive Pivot Links
    pivot_links = {}
    if chosen_platform == "twitter":
        pivot_links["Wayback Machine (Target Tweet/Status)"] = f"https://web.archive.org/web/*/https://twitter.com/*/status/{snowflake_id}"
        pivot_links["Archive.today Lookup"] = f"https://archive.today/https://twitter.com/*/status/{snowflake_id}"
        pivot_links["Google Dork (Mentions to Numeric ID)"] = f"https://www.google.com/search?q={urllib.parse.quote(f'to:{snowflake_id}')}"
        pivot_links["Twitter Direct URL Status"] = f"https://twitter.com/i/status/{snowflake_id}"
    else:
        pivot_links["Discord Lookup (Discord.id)"] = f"https://discord.id/?prefill={snowflake_id}"
        pivot_links["DiscordLookup Tool"] = f"https://discordlookup.com/user/{snowflake_id}"

    return {
        "success": True,
        "snowflake_id": str(snowflake_id),
        "platform": chosen_platform.capitalize(),
        "epoch": epoch_name,
        "timestamp_ms": timestamp_ms,
        "created_utc": date_str_utc,
        "created_wib": date_str_wib,
        "iso_timestamp": iso_str,
        "date_only": date_only,
        "internal_worker_id": internal_worker_id,
        "internal_process_id": internal_process_id,
        "sequence": sequence,
        "pivot_links": pivot_links
    }


def generate_immutable_pivots(target_id: str, platform: str) -> dict:
    """
    Generates OSINT pivot links for platform-specific immutable identifiers
    such as Instagram PK IDs, Telegram User IDs, and Google GAIA / Contributor IDs.
    """
    cleaned_id = str(target_id).strip()
    platform_key = platform.lower().strip()

    if platform_key in ["instagram", "ig"]:
        return {
            "success": True,
            "platform": "Instagram (PK / Numeric User ID)",
            "target_id": cleaned_id,
            "description": "ID numerik permanen Instagram yang tidak berubah meskipun pelaku mengganti username.",
            "pivots": {
                "Picuki Mirror Viewer": f"https://www.picuki.com/profile/{cleaned_id}",
                "Imginn Instagram Mirror": f"https://imginn.com/",
                "Google Dork (Histori Username Lama)": f"https://www.google.com/search?q={urllib.parse.quote(f'site:instagram.com \"{cleaned_id}\"')}",
                "Archive.today Profil Instagram": f"https://archive.today/https://www.instagram.com/*/"
            }
        }

    elif platform_key in ["telegram", "tg"]:
        return {
            "success": True,
            "platform": "Telegram (Peer / User ID)",
            "target_id": cleaned_id,
            "description": "ID numerik akun Telegram yang terikat permanen ke akun pengguna.",
            "pivots": {
                "TGStat Global Search": f"https://tgstat.com/search?q={urllib.parse.quote(cleaned_id)}",
                "Telemetr Analytics": f"https://telemetr.io/en/channels?search={urllib.parse.quote(cleaned_id)}",
                "Direct Telegram Protocol": f"tg://user?id={cleaned_id}",
                "Google Dork (Riwayat Pesan di Channel/Grup)": f"https://www.google.com/search?q={urllib.parse.quote(f'site:t.me \"{cleaned_id}\"')}"
            }
        }

    elif platform_key in ["google", "gaia", "maps"]:
        return {
            "success": True,
            "platform": "Google Contributor / GAIA ID",
            "target_id": cleaned_id,
            "description": "ID numerik unik 21 digit Google yang mengekspos ulasan Google Maps, foto lokal, dan kontribusi publik.",
            "pivots": {
                "Google Maps Contributor Profile": f"https://www.google.com/maps/contrib/{cleaned_id}",
                "Google Album Archive": f"https://get.google.com/albumarchive/{cleaned_id}",
                "Google Reviews Footprint Dork": f"https://www.google.com/search?q={urllib.parse.quote(f'site:google.com/maps/contrib/{cleaned_id}')}",
                "Peta Ulasan Lokal Dork": f"https://www.google.com/search?q={urllib.parse.quote(f'\"google.com/maps/contrib/{cleaned_id}\"')}"
            }
        }

    return {
        "success": False,
        "error": f"Platform '{platform}' tidak dikenali. Pilih salah satu: 'twitter', 'discord', 'instagram', 'telegram', 'google'."
    }


def analyze_social_graph_overlap(list_a: list[str], list_b: list[str], label_a: str = "Akun A", label_b: str = "Akun B") -> dict:
    """
    Computes set intersection, union, and Jaccard similarity coefficient
    between two follower/following circles to detect sock-puppet / burner account linkages.
    """
    set_a = {item.strip().lstrip("@").lower() for item in list_a if item.strip()}
    set_b = {item.strip().lstrip("@").lower() for item in list_b if item.strip()}

    if not set_a or not set_b:
        return {
            "success": False,
            "error": "Kedua daftar akun pengikut/mengikuti harus memiliki setidaknya satu username."
        }

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)

    jaccard_similarity = (len(intersection) / len(union)) * 100.0 if union else 0.0

    # Risk / Correlation assessment
    if jaccard_similarity >= 30.0 or len(intersection) >= 15:
        risk_level = "SANGAT TINGGI"
        risk_desc = "Irisan koneksi sangat padat. Kemungkinan besar kedua akun berasal dari lingkungan sosial atau pengguna fisik yang sama."
    elif jaccard_similarity >= 10.0 or len(intersection) >= 5:
        risk_level = "SEDANG"
        risk_desc = "Terdapat beberapa koneksi bersama yang relevan. Akun mutual ini merupakan kandidat utama lingkaran pertemanan inti."
    elif len(intersection) > 0:
        risk_level = "RENDAH"
        risk_desc = "Terdapat sedikit koneksi bersama. Periksa apakah akun mutual adalah influencer besar atau akun pertemanan privat."
    else:
        risk_level = "TIDAK TERDETEKSI"
        risk_desc = "Tidak ditemukan akun mutual yang sama di antara kedua daftar yang dimasukkan."

    return {
        "success": True,
        "label_a": label_a,
        "count_a": len(set_a),
        "label_b": label_b,
        "count_b": len(set_b),
        "total_unique": len(union),
        "shared_count": len(intersection),
        "similarity_index": round(jaccard_similarity, 2),
        "correlation_level": risk_level,
        "assessment": risk_desc,
        "shared_accounts": sorted(list(intersection))
    }
