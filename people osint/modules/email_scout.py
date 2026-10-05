import re
import hashlib
import urllib.parse
import requests

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def scout_email_identity(email: str, timeout: int = 12) -> dict:
    cleaned = email.strip().lower()
    if not cleaned:
        return {"success": False, "error": "Email tidak boleh kosong."}

    if not EMAIL_REGEX.match(cleaned):
        return {"success": False, "error": f"Format email tidak valid: '{cleaned}'"}

    # 1. Gravatar Public Profile Extraction
    gravatar_data = _check_gravatar(cleaned, timeout=timeout)

    # 2. XposedOrNot Breach Intelligence
    breach_data = _check_breaches(cleaned, timeout=timeout)

    # 3. Pivot Verification Resources
    pivot_links = _generate_pivot_links(cleaned)

    return {
        "success": True,
        "email": cleaned,
        "gravatar": gravatar_data,
        "breaches": breach_data,
        "pivot_links": pivot_links
    }


def _check_gravatar(email: str, timeout: int = 8) -> dict:
    email_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
    api_url = f"https://www.gravatar.com/{email_hash}.json"
    headers = {"User-Agent": "PeopleScout-OSINT/2.0"}

    try:
        r = requests.get(api_url, headers=headers, timeout=timeout)
        if r.status_code == 200:
            payload = r.json()
            entries = payload.get("entry", [])
            if entries:
                entry = entries[0]
                return {
                    "found": True,
                    "profile_url": f"https://gravatar.com/{email_hash}",
                    "avatar_url": entry.get("thumbnailUrl") or f"https://www.gravatar.com/avatar/{email_hash}?s=400",
                    "display_name": entry.get("displayName") or "N/A",
                    "preferred_username": entry.get("preferredUsername") or "N/A",
                    "about_me": entry.get("aboutMe") or "N/A",
                    "location": entry.get("currentLocation") or "N/A",
                    "linked_accounts": [u.get("value") for u in entry.get("urls", []) if u.get("value")]
                }
    except Exception:
        pass

    return {
        "found": False,
        "avatar_url": f"https://www.gravatar.com/avatar/{email_hash}?d=mp&s=400"
    }


def _check_breaches(email: str, timeout: int = 12) -> dict:
    encoded = urllib.parse.quote(email)
    api_url = f"https://api.xposedornot.com/v1/breach-analytics?email={encoded}"
    headers = {
        "User-Agent": "PeopleScout-OSINT/2.0",
        "Accept": "application/json"
    }

    try:
        resp = requests.get(api_url, headers=headers, timeout=timeout)
    except Exception as e:
        return {
            "status": "ERROR",
            "message": f"Gagal terhubung ke database kebocoran: {e}",
            "count": 0,
            "items": []
        }

    if resp.status_code == 404:
        return {
            "status": "CLEAN",
            "count": 0,
            "risk_level": "CLEAN",
            "risk_message": "Email tidak ditemukan di database kebocoran publik.",
            "password_metrics": {},
            "exposed_fields": [],
            "items": []
        }

    if resp.status_code != 200:
        return {
            "status": "ERROR",
            "message": f"Respon API tidak normal (HTTP {resp.status_code})",
            "count": 0,
            "items": []
        }

    try:
        data = resp.json()
    except Exception:
        return {"status": "ERROR", "message": "Gagal membaca format JSON", "count": 0, "items": []}

    exposed_obj = data.get("ExposedBreaches") or {}
    raw_breaches = exposed_obj.get("breaches_details", []) if isinstance(exposed_obj, dict) else []

    all_fields = set()
    parsed_items = []
    has_plain = False
    has_easy = False

    for b in raw_breaches:
        x_fields = [f.strip() for f in (b.get("xposed_data") or "").split(";") if f.strip()]
        for f in x_fields:
            all_fields.add(f)

        prisk = str(b.get("password_risk") or "").lower()
        if "plaintext" in prisk:
            has_plain = True
        elif "easytocrack" in prisk:
            has_easy = True

        parsed_items.append({
            "name": b.get("breach") or "Tidak diketahui",
            "domain": b.get("domain") or "N/A",
            "industry": b.get("industry") or "General",
            "year": str(b.get("xposed_date") or "N/A"),
            "records": b.get("xposed_records") or 0,
            "password_risk": b.get("password_risk") or "N/A",
            "exposed_fields": x_fields,
            "summary": b.get("details") or ""
        })

    metrics = data.get("BreachMetrics") or {}
    pw_strength = (metrics.get("passwords_strength") or [{}])[0]

    if has_plain or pw_strength.get("PlainText", 0) > 0:
        risk_level = "CRITICAL"
        risk_msg = "Sangat Berbahaya: Ditemukan kebocoran password dalam format PlainText!"
    elif has_easy or any("password" in f.lower() for f in all_fields):
        risk_level = "HIGH"
        risk_msg = "Tinggi: Kredensial password dan data pribadi sensitif terekspos."
    elif len(parsed_items) > 3:
        risk_level = "MEDIUM"
        risk_msg = "Moderat: Email terlibat dalam beberapa insiden kebocoran akun."
    elif parsed_items:
        risk_level = "LOW"
        risk_msg = "Rendah: Terdaftar dalam sedikit kebocoran tanpa eksposur password kritis."
    else:
        risk_level = "CLEAN"
        risk_msg = "Bersih: Tidak ada insiden kebocoran terdeteksi."

    return {
        "status": "EXPOSED" if parsed_items else "CLEAN",
        "count": len(parsed_items),
        "risk_level": risk_level,
        "risk_message": risk_msg,
        "password_metrics": pw_strength,
        "exposed_fields": sorted(list(all_fields)),
        "items": parsed_items
    }


def _generate_pivot_links(email: str) -> dict:
    encoded = urllib.parse.quote(email)
    domain = email.split("@")[-1] if "@" in email else ""
    return {
        "Epieos Google Account Recon": f"https://epieos.com/?q={encoded}",
        "Hunter.io Email Verifier": f"https://hunter.io/verify/{encoded}",
        "Have I Been Pwned Profile": f"https://haveibeenpwned.com/account/{encoded}",
        "Google Dork Email Search": f"https://www.google.com/search?q=%22{encoded}%22",
        "Mailbox Domain MX Health": f"https://mxtoolbox.com/SuperTool.aspx?action=mx%3a{domain}"
    }
