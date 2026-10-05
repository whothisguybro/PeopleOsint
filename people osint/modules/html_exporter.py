import os
import datetime


def generate_person_dossier_html(target_info: dict, output_filepath: str) -> str:
    target_name = target_info.get("name") or target_info.get("username") or "Target Person"
    created_time = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Profile & Avatar
    avatar_url = target_info.get("avatar_url") or "https://ui-avatars.com/api/?name=" + target_name.replace(" ", "+") + "&background=00e575&color=000&size=200"
    bio = target_info.get("bio") or "Tidak ada deskripsi bio yang terdeteksi."
    location = target_info.get("location") or "Tidak diketahui"
    company = target_info.get("company") or "Tidak terdeteksi"

    # Social Profiles
    profiles = target_info.get("profiles", [])
    profile_cards_html = []
    for p in profiles:
        plat = p.get("platform", "Unknown")
        cat = p.get("category", "General")
        url = p.get("url", "#")
        profile_cards_html.append(f"""
        <div class="profile-card">
            <div class="profile-top">
                <span class="plat-name">{plat}</span>
                <span class="plat-cat">{cat}</span>
            </div>
            <a href="{url}" target="_blank" rel="noopener noreferrer" class="plat-link">{url}</a>
        </div>
        """)

    profiles_section = ""
    if profile_cards_html:
        profiles_section = f"""
        <section class="section-block">
            <h2 class="section-title">Akun Digital Terkonfirmasi ({len(profile_cards_html)})</h2>
            <div class="profile-grid">
                {"".join(profile_cards_html)}
            </div>
        </section>
        """

    # Email & Breaches
    email_data = target_info.get("email_data", {})
    email_section = ""
    if email_data and email_data.get("email"):
        br_items = email_data.get("breaches", {}).get("items", [])
        br_rows = []
        for b in br_items[:15]:
            fields = ", ".join(b.get("exposed_fields", [])) or "Email"
            br_rows.append(f"""
            <tr>
                <td style="font-weight: 600; color: #fff;">{b.get('name')}</td>
                <td>{b.get('year')}</td>
                <td style="color: #ff4d4d;">{b.get('password_risk')}</td>
                <td>{fields}</td>
            </tr>
            """)

        table_html = f"""
        <table class="data-table">
            <thead>
                <tr>
                    <th>Entitas Kebocoran</th>
                    <th>Tahun</th>
                    <th>Risiko Password</th>
                    <th>Data Terekspos</th>
                </tr>
            </thead>
            <tbody>
                {"".join(br_rows)}
            </tbody>
        </table>
        """ if br_rows else "<p style='color: #00e575; padding: 12px 0;'>✓ Email bersih, tidak ditemukan pada database kebocoran publik.</p>"

        email_section = f"""
        <section class="section-block">
            <h2 class="section-title">Audit Kredensial & Kebocoran Email: {email_data.get('email')}</h2>
            <div class="card-box">
                {table_html}
            </div>
        </section>
        """

    # Phone Section
    phone_data = target_info.get("phone_data", {})
    phone_section = ""
    if phone_data and phone_data.get("e164"):
        phone_section = f"""
        <section class="section-block">
            <h2 class="section-title">Telekomunikasi & Profil Nomor HP: {phone_data.get('e164')}</h2>
            <div class="card-box">
                <div class="info-grid">
                    <div><span class="dim">Operator Seluler:</span> <strong>{phone_data.get('carrier')}</strong></div>
                    <div><span class="dim">Tipe Nomor:</span> <strong>{phone_data.get('line_type')}</strong></div>
                    <div><span class="dim">Wilayah:</span> <strong>{phone_data.get('location')}</strong></div>
                    <div><span class="dim">Zona Waktu:</span> <strong>{', '.join(phone_data.get('timezones', []))}</strong></div>
                </div>
                <div style="margin-top: 16px; display: flex; gap: 12px; flex-wrap: wrap;">
                    <a href="{phone_data.get('lookup_links', {}).get('Direct WhatsApp Chat', '#')}" target="_blank" class="btn btn-mint">Chat WhatsApp &rarr;</a>
                    <a href="{phone_data.get('lookup_links', {}).get('Truecaller Web Search', '#')}" target="_blank" class="btn btn-outline">Cek Truecaller &rarr;</a>
                </div>
            </div>
        </section>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>People OSINT Dossier: {target_name}</title>
    <style>
        :root {{
            --bg: #0b0f19;
            --surface: #161b22;
            --border: #30363d;
            --mint: #00e575;
            --text: #f4efe6;
            --muted: #8b949e;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            padding: 32px 20px;
            line-height: 1.5;
        }}
        .container {{ max-width: 1050px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .brand {{
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--mint);
            font-weight: 700;
        }}
        h1 {{
            font-size: 26px;
            color: #fff;
            margin-top: 4px;
        }}
        .timestamp {{
            font-size: 13px;
            color: var(--muted);
            font-family: monospace;
        }}
        .profile-summary {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 24px;
            display: flex;
            gap: 24px;
            align-items: center;
            margin-bottom: 32px;
            flex-wrap: wrap;
        }}
        .avatar-img {{
            width: 96px;
            height: 96px;
            border-radius: 50%;
            border: 2px solid var(--mint);
            object-fit: cover;
        }}
        .summary-info {{ flex: 1; min-width: 260px; }}
        .summary-name {{ font-size: 20px; font-weight: 700; color: #fff; margin-bottom: 6px; }}
        .summary-bio {{ color: var(--muted); font-size: 14px; margin-bottom: 10px; }}
        .summary-meta {{ display: flex; gap: 16px; font-size: 13px; color: var(--muted); flex-wrap: wrap; }}
        .section-block {{ margin-bottom: 36px; }}
        .section-title {{
            font-size: 18px;
            color: var(--mint);
            padding-bottom: 8px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 18px;
        }}
        .profile-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 14px;
        }}
        .profile-card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 14px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .profile-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .plat-name {{ font-weight: 700; color: #fff; font-size: 14px; }}
        .plat-cat {{ font-size: 11px; color: var(--muted); background: #0d1117; padding: 2px 6px; border-radius: 4px; }}
        .plat-link {{
            color: #58a6ff;
            text-decoration: none;
            font-size: 12px;
            word-break: break-all;
        }}
        .plat-link:hover {{ text-decoration: underline; }}
        .card-box {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 20px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 14px;
            font-size: 14px;
        }}
        .dim {{ color: var(--muted); }}
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }}
        .data-table th, .data-table td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }}
        .data-table th {{ color: var(--muted); text-transform: uppercase; font-size: 11px; }}
        .btn {{
            font-size: 13px;
            font-weight: 600;
            padding: 8px 16px;
            border-radius: 5px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
        }}
        .btn-mint {{ background: var(--mint); color: #000; }}
        .btn-mint:hover {{ background: #00c765; }}
        .btn-outline {{ background: transparent; color: #fff; border: 1px solid var(--border); }}
        .btn-outline:hover {{ background: var(--border); }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <div class="brand">PeopleScout OSINT Dossier</div>
                <h1>Identitas Target: {target_name}</h1>
            </div>
            <div class="timestamp">Generated: {created_time}</div>
        </header>

        <div class="profile-summary">
            <img src="{avatar_url}" alt="Target Avatar" class="avatar-img" onerror="this.src='https://ui-avatars.com/api/?name={target_name}&background=00e575&color=000&size=200'">
            <div class="summary-info">
                <div class="summary-name">{target_name}</div>
                <div class="summary-bio">{bio}</div>
                <div class="summary-meta">
                    <span><strong>Lokasi:</strong> {location}</span>
                    <span><strong>Afiliasi:</strong> {company}</span>
                </div>
            </div>
        </div>

        {profiles_section}
        {email_section}
        {phone_section}
    </div>
</body>
</html>
"""
    with open(output_filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_filepath
