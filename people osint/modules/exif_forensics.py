"""
PeopleScout v2.0 - Image & EXIF Forensic Investigation Engine
Extracts camera metadata, software manipulation footprints, GPS coordinates,
and generates direct Google Maps and SunCalc chronolocation pivot links.
"""

import os
import datetime
from PIL import Image, ExifTags


def _convert_to_degrees(value) -> float | None:
    """
    Helper function to convert GPS DMS (Degrees, Minutes, Seconds)
    into decimal degrees format.
    """
    try:
        if isinstance(value, (list, tuple)) and len(value) >= 3:
            deg = float(value[0])
            minutes = float(value[1])
            sec = float(value[2])
            return deg + (minutes / 60.0) + (sec / 3600.0)
        elif isinstance(value, (int, float)):
            return float(value)
    except Exception:
        pass
    return None


def analyze_image_forensics(image_path: str) -> dict:
    """
    Parses EXIF and GPS metadata from an image file, detects software tampering,
    and returns geolocation coordinates and mapping links.
    """
    clean_path = os.path.abspath(image_path.strip().strip('"').strip("'"))

    if not os.path.exists(clean_path):
        return {
            "success": False,
            "error": f"Berkas gambar tidak ditemukan pada path: {clean_path}"
        }

    try:
        with Image.open(clean_path) as img:
            file_size_kb = round(os.path.getsize(clean_path) / 1024, 2)
            dimensions = f"{img.width}x{img.height} px"
            image_format = img.format or "UNKNOWN"
            color_mode = img.mode

            raw_exif = img.getexif()
            if not raw_exif:
                # Fallback to legacy _getexif if available
                if hasattr(img, "_getexif"):
                    legacy_exif = img._getexif()
                    raw_exif = legacy_exif or {}

            # Dictionary to store readable tags
            exif_data = {}
            gps_data = {}

            if raw_exif:
                for tag_id, value in raw_exif.items():
                    tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
                    # Handle GPSInfo sub-IFD
                    if tag_name == "GPSInfo" or tag_id == 0x8825:
                        if hasattr(raw_exif, "get_ifd"):
                            try:
                                gps_ifd = raw_exif.get_ifd(ExifTags.IFD.GPSInfo)
                                for gps_id, gps_val in gps_ifd.items():
                                    sub_tag = ExifTags.GPSTAGS.get(gps_id, str(gps_id))
                                    gps_data[sub_tag] = gps_val
                            except Exception:
                                pass
                        if not gps_data and isinstance(value, dict):
                            for sub_id, sub_val in value.items():
                                sub_tag = ExifTags.GPSTAGS.get(sub_id, str(sub_id))
                                gps_data[sub_tag] = sub_val
                    else:
                        # Avoid huge binary byte dumps
                        if isinstance(value, (bytes, bytearray)):
                            if len(value) > 64:
                                exif_data[tag_name] = f"<binary blob {len(value)} bytes>"
                            else:
                                try:
                                    exif_data[tag_name] = value.decode("utf-8", errors="replace").strip()
                                except Exception:
                                    exif_data[tag_name] = str(value)
                        else:
                            exif_data[tag_name] = value

    except Exception as err:
        return {
            "success": False,
            "error": f"Gagal membaca metadata gambar: {err}"
        }

    # Extract Camera & Hardware info
    make = str(exif_data.get("Make", "")).strip()
    model = str(exif_data.get("Model", "")).strip()
    lens_model = str(exif_data.get("LensModel", "")).strip()
    software = str(exif_data.get("Software", "")).strip()
    date_taken = str(exif_data.get("DateTimeOriginal") or exif_data.get("DateTime") or "").strip()

    # Extract GPS Coordinates
    latitude = None
    longitude = None
    altitude = None

    if gps_data:
        lat_raw = gps_data.get("GPSLatitude")
        lat_ref = gps_data.get("GPSLatitudeRef")
        lon_raw = gps_data.get("GPSLongitude")
        lon_ref = gps_data.get("GPSLongitudeRef")
        alt_raw = gps_data.get("GPSAltitude")

        if lat_raw and lat_ref:
            dec_lat = _convert_to_degrees(lat_raw)
            if dec_lat is not None:
                if str(lat_ref).upper() == "S":
                    dec_lat = -dec_lat
                latitude = round(dec_lat, 6)

        if lon_raw and lon_ref:
            dec_lon = _convert_to_degrees(lon_raw)
            if dec_lon is not None:
                if str(lon_ref).upper() == "W":
                    dec_lon = -dec_lon
                longitude = round(dec_lon, 6)

        if alt_raw is not None:
            try:
                altitude = round(float(alt_raw), 2)
            except Exception:
                pass

    # Geolocation Mapping URLs
    geo_links = {}
    if latitude is not None and longitude is not None:
        geo_links["Google Maps Pin"] = f"https://www.google.com/maps?q={latitude},{longitude}"
        geo_links["OpenStreetMap"] = f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map=16/{latitude}/{longitude}"
        geo_links["Google Earth View"] = f"https://earth.google.com/web/search/{latitude},{longitude}"

        # SunCalc Chronolocation link
        if date_taken:
            try:
                parts = date_taken.replace("-", ":").split(" ")
                date_part = parts[0].replace(":", ".")
                time_part = parts[1] if len(parts) > 1 else "12:00"
                geo_links["SunCalc Solar Angle Calculator"] = f"https://www.suncalc.org/#/{latitude},{longitude},16/{date_part}/{time_part}"
            except Exception:
                geo_links["SunCalc Solar Angle Calculator"] = f"https://www.suncalc.org/#/{latitude},{longitude},16"
        else:
            geo_links["SunCalc Solar Angle Calculator"] = f"https://www.suncalc.org/#/{latitude},{longitude},16"

    # Forensic Tampering / Compression Assessment
    tamper_flags = []
    suspicious_keywords = ["photoshop", "gimp", "lightroom", "canva", "snapseed", "picsart", "vsco", "pixlr"]
    if software:
        for kw in suspicious_keywords:
            if kw in software.lower():
                tamper_flags.append(f"Terdeteksi jejak manipulasi/editing menggunakan perangkat lunak: '{software}'")

    has_exif = bool(exif_data or gps_data)
    if not has_exif:
        compression_notes = (
            "Tidak ditemukan metadata EXIF pada berkas ini. Kemungkinan besar berkas telah "
            "dibersihkan otomatis oleh media sosial (Instagram, WhatsApp, X/Twitter, TikTok) "
            "saat diunggah, atau merupakan hasil tangkapan layar (screenshot)."
        )
    else:
        compression_notes = "Metadata EXIF asli berhasil diekstraksi dari berkas."

    return {
        "success": True,
        "file_name": os.path.basename(clean_path),
        "file_path": clean_path,
        "file_size_kb": file_size_kb,
        "dimensions": dimensions,
        "format": image_format,
        "color_mode": color_mode,
        "has_exif": has_exif,
        "device_make": make or "Tidak tercatat",
        "device_model": model or "Tidak tercatat",
        "lens_model": lens_model or "Tidak tercatat",
        "software": software or "Kamera Bawaan / Tidak Tertera",
        "date_taken": date_taken or "Tidak tercatat",
        "gps": {
            "has_gps": (latitude is not None and longitude is not None),
            "latitude": latitude,
            "longitude": longitude,
            "altitude_meters": altitude,
            "geo_links": geo_links
        },
        "tamper_assessment": {
            "is_flagged": len(tamper_flags) > 0,
            "flags": tamper_flags,
            "notes": compression_notes
        },
        "raw_tags_count": len(exif_data) + len(gps_data)
    }
