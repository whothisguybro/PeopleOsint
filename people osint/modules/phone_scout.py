import urllib.parse
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

NUMBER_TYPE_MAP = {
    0: "FIXED_LINE (Telepon Rumah / Kantor)",
    1: "MOBILE (Nomor HP Seluler)",
    2: "FIXED_LINE_OR_MOBILE (Nomor Tetap / Seluler)",
    3: "TOLL_FREE (Bebas Pulsa)",
    4: "PREMIUM_RATE (Tarif Premium)",
    5: "SHARED_COST (Biaya Bagi)",
    6: "VOIP (Virtual / Internet VoIP)",
    7: "PERSONAL_NUMBER (Nomor Personal)",
    8: "PAGER (Pager)",
    9: "UAN (Universal Access Number)",
    10: "VOICEMAIL (Kotak Suara)",
    99: "UNKNOWN (Tidak Dikenal)"
}


def scout_phone_number(raw_phone: str, default_region: str = "ID") -> dict:
    cleaned = raw_phone.strip()
    if not cleaned:
        return {"success": False, "error": "Nomor telepon tidak boleh kosong."}

    # Normalize Indonesian local prefix 08xx to +628xx if no + is provided
    if cleaned.startswith("08") and default_region == "ID":
        cleaned = "+62" + cleaned[1:]
    elif not cleaned.startswith("+") and not cleaned.startswith("00"):
        cleaned = "+" + cleaned

    try:
        parsed = phonenumbers.parse(cleaned, default_region)
    except Exception as e:
        return {"success": False, "error": f"Format nomor telepon tidak valid: {e}"}

    is_valid = phonenumbers.is_valid_number(parsed)
    is_possible = phonenumbers.is_possible_number(parsed)

    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    intl_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    nat_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
    country_code = parsed.country_code
    national_number = parsed.national_number

    # Geocoding & Region
    region_id = geocoder.description_for_number(parsed, "id")
    region_en = geocoder.description_for_number(parsed, "en")
    location = region_id or region_en or "Tidak diketahui"

    # Carrier / Operator Name
    carrier_id = carrier.name_for_number(parsed, "id")
    carrier_en = carrier.name_for_number(parsed, "en")
    carrier_name = carrier_id or carrier_en or "Tidak terdeteksi (atau nomor virtual/VoIP)"

    # Timezones
    tz_list = list(timezone.time_zones_for_number(parsed))

    # Line Type
    raw_type = phonenumbers.number_type(parsed)
    line_type = NUMBER_TYPE_MAP.get(raw_type, "UNKNOWN")

    # Pivot OSINT Links
    encoded_e164 = urllib.parse.quote(e164)
    clean_digits = e164.lstrip("+")

    lookup_links = {
        "Direct WhatsApp Chat": f"https://wa.me/{clean_digits}",
        "Direct Telegram Chat": f"https://t.me/+{clean_digits}",
        "Truecaller Web Search": f"https://www.truecaller.com/search/{clean_digits}",
        "Sync.me Web Lookup": f"https://sync.me/search/?number={encoded_e164}",
        "Should I Answer Lookup": f"https://www.shouldianswer.com/phone-number/{clean_digits}",
        "Google Dork Phone Search": f"https://www.google.com/search?q=%22{encoded_e164}%22+OR+%22{urllib.parse.quote(intl_fmt)}%22"
    }

    return {
        "success": True,
        "raw_input": raw_phone,
        "is_valid": is_valid,
        "is_possible": is_possible,
        "e164": e164,
        "international_format": intl_fmt,
        "national_format": nat_fmt,
        "country_code": f"+{country_code}",
        "national_number": str(national_number),
        "location": location,
        "carrier": carrier_name,
        "line_type": line_type,
        "timezones": tz_list,
        "lookup_links": lookup_links
    }
