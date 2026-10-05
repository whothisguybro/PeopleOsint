#!/usr/bin/env python3
"""
PeopleScout v2.0 - Deep Identity, Username & People Intelligence Engine
Daytona Minimalist Developer CLI Aesthetic
"""

import os
import sys
import json
import argparse
import webbrowser

# Ensure Windows terminal renders UTF-8 checkmarks and symbols without codec errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.markup import escape

import pyfiglet

from modules.username_recon import scout_username_all
from modules.email_scout import scout_email_identity
from modules.phone_scout import scout_phone_number
from modules.name_search import generate_name_dorks
from modules.profile_grabber import grab_profile_metadata
from modules.html_exporter import generate_person_dossier_html
from modules.socmint_forensics import decode_snowflake_id, generate_immutable_pivots, analyze_social_graph_overlap
from modules.exif_forensics import analyze_image_forensics

console = Console()

try:
    _fig = pyfiglet.Figlet(font="big_money-se")
    JAPARJIR_BANNER = _fig.renderText("japarjir")
except Exception:
    JAPARJIR_BANNER = "japarjir"

# Daytona Aesthetic Palette
MINT = "#00e575"
TEXT_COLOR = "#f4efe6"
MUTED_COLOR = "#888888"
BORDER_DARK = "#2e2e2e"
AMBER = "#e5a50a"
RED = "#ff4d4d"


def render_banner():
    console.print(Text(JAPARJIR_BANNER.rstrip(), style=f"bold {MINT}"))
    console.print(
        Text.assemble(
            (" PEOPLE SCOUT ", f"bold black on {MINT}"),
            ("  v2.0   ", "bold white"),
            ("Deep Identity, Username & People Intelligence Engine", MUTED_COLOR)
        )
    )
    console.print()


def make_card(title: str, content, border_color: str = BORDER_DARK) -> Panel:
    return Panel(
        content,
        title=f"[bold black on {MINT}] {title} [/bold black on {MINT}]",
        title_align="left",
        box=box.ROUNDED,
        border_style=border_color,
        padding=(0, 1)
    )


def make_table(title: str | None = None, show_header: bool = True) -> Table:
    return Table(
        title=title,
        title_style="bold white",
        title_justify="left",
        show_header=show_header,
        box=box.SIMPLE_HEAD,
        border_style=BORDER_DARK,
        header_style=f"bold {MINT}",
        padding=(0, 1)
    )


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def ask_input(prompt_text: str) -> str:
    console.print(f"[bold {MINT}]❯[/bold {MINT}] [bold white]{prompt_text}[/bold white]", end="")
    try:
        return input().strip()
    except (KeyboardInterrupt, EOFError):
        return "b"


# -------------------------------------------------------------
# Handlers
# -------------------------------------------------------------

def handle_username(username: str, output_json: bool):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Scanning 50+ platform digital identity for @{username}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = scout_username_all(username)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal melacak username:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    # Summary Card
    summary_card = Table(box=None, padding=(0, 1), show_header=False)
    summary_card.add_column("Key", style=MUTED_COLOR, width=22)
    summary_card.add_column("Value", style="white")

    summary_card.add_row("Target Username", f"[bold white]@{data['username']}[/bold white]")
    summary_card.add_row("Total Platform Ditelusuri", f"{data['total_probed']} platform")
    summary_card.add_row("Profil Terkonfirmasi", f"[bold {MINT}]{data['total_found']} akun ditemukan[/bold {MINT}]")

    cat_stats = ", ".join([f"{k}: {v}" for k, v in data.get("category_counts", {}).items()]) or "N/A"
    summary_card.add_row("Distribusi Kategori", cat_stats)

    console.print(make_card("Username Footprint Intelligence", summary_card))
    console.print()

    # Profiles Table
    profiles = data.get("profiles", [])
    if profiles:
        table = make_table(f"Discovered Profiles ({len(profiles)})")
        table.add_column("No", justify="center", style=f"bold {MINT}", width=4)
        table.add_column("Platform", style="bold white", width=20)
        table.add_column("Category", style=MUTED_COLOR, width=26)
        table.add_column("Profile URL", style="cyan", no_wrap=False, overflow="fold")

        for idx, p in enumerate(profiles, 1):
            table.add_row(
                str(idx),
                escape(p["platform"]),
                escape(p["category"]),
                f"[underline]{escape(p['url'])}[/underline]"
            )

        console.print(table)
        console.print()
    else:
        console.print(f"[{AMBER}]Tidak ditemukan profil terkonfirmasi untuk username @{username}.[/{AMBER}]\n")


def handle_email(email: str, output_json: bool):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Auditing email identity & breach history: {email}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = scout_email_identity(email)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal melacak email:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    # Gravatar Card
    grav = data.get("gravatar", {})
    card_table = Table(box=None, padding=(0, 1), show_header=False)
    card_table.add_column("Key", style=MUTED_COLOR, width=22)
    card_table.add_column("Value", style="white")

    card_table.add_row("Audited Email", f"[bold white]{data['email']}[/bold white]")
    if grav.get("found"):
        card_table.add_row("Gravatar Status", f"[bold {MINT}]PROFIL PUBLIK DITEMUKAN[/bold {MINT}]")
        card_table.add_row("Display Name", escape(grav.get("display_name", "N/A")))
        card_table.add_row("Preferred Username", escape(grav.get("preferred_username", "N/A")))
        card_table.add_row("About Me / Bio", escape(grav.get("about_me", "N/A")))
        card_table.add_row("Location", escape(grav.get("location", "N/A")))
        card_table.add_row("Avatar URL", f"[underline]{escape(grav.get('avatar_url', 'N/A'))}[/underline]")
    else:
        card_table.add_row("Gravatar Status", "[dim]Tidak ada akun Gravatar terdaftar[/dim]")

    console.print(make_card("Email Identity & Public Avatar", card_table))
    console.print()

    # Breaches
    br = data.get("breaches", {})
    risk = br.get("risk_level", "CLEAN")
    r_color = RED if risk in ["CRITICAL", "HIGH"] else (AMBER if risk == "MEDIUM" else MINT)

    br_table = Table(box=None, padding=(0, 1), show_header=False)
    br_table.add_column("Key", style=MUTED_COLOR, width=22)
    br_table.add_column("Value", style="white")

    br_table.add_row("Insiden Kebocoran", f"[bold {r_color}]{br.get('count', 0)} insiden terdeteksi[/bold {r_color}]")
    br_table.add_row("Tingkat Risiko", f"[bold {r_color}]{risk} - {escape(br.get('risk_message', ''))}[/bold {r_color}]")

    pw_m = br.get("password_metrics", {})
    if pw_m:
        br_table.add_row("Password Vulnerability", f"PlainText: {pw_m.get('PlainText', 0)} | Easy to Crack: {pw_m.get('EasyToCrack', 0)}")

    exp_f = br.get("exposed_fields", [])
    if exp_f:
        br_table.add_row("Data Terekspos", ", ".join([f"[bold white]{escape(f)}[/bold white]" for f in exp_f]))

    console.print(make_card("Breach & Security Exposure", br_table))
    console.print()

    # Pivot Links
    pivot_links = data.get("pivot_links", {})
    if pivot_links:
        pv_table = make_table("Investigative Pivot & Verification Resources")
        pv_table.add_column("Resource Platform", style="bold white", width=28)
        pv_table.add_column("Direct Pivot URL", style="cyan", no_wrap=False, overflow="fold")

        for name, url in pivot_links.items():
            pv_table.add_row(name, f"[underline]{escape(url)}[/underline]")

        console.print(pv_table)
        console.print()


def handle_phone(phone: str, output_json: bool):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Auditing phone number intelligence: {phone}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = scout_phone_number(phone)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal menganalisis nomor telepon:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    card_table = Table(box=None, padding=(0, 1), show_header=False)
    card_table.add_column("Key", style=MUTED_COLOR, width=22)
    card_table.add_column("Value", style="white")

    card_table.add_row("Input Target", escape(data["raw_input"]))
    card_table.add_row("E.164 Standard", f"[bold {MINT}]{data['e164']}[/bold {MINT}]")
    card_table.add_row("International Format", data["international_format"])
    card_table.add_row("National Format", data["national_format"])
    card_table.add_row("Carrier / Operator", f"[bold white]{escape(data['carrier'])}[/bold white]")
    card_table.add_row("Line Type", data["line_type"])
    card_table.add_row("Geographic Region", data["location"])
    tzs = ", ".join(data.get("timezones", [])) or "N/A"
    card_table.add_row("Timezone(s)", tzs)

    valid_badge = f"[bold {MINT}]VALID[/bold {MINT}]" if data["is_valid"] else f"[bold {RED}]INVALID[/bold {RED}]"
    card_table.add_row("Validation Status", valid_badge)

    console.print(make_card(f"Phone Intelligence: {data['e164']}", card_table))
    console.print()

    link_table = make_table("OSINT Direct Lookups & Pivot Links")
    link_table.add_column("Target Platform / Service", style="bold white", width=26)
    link_table.add_column("Direct Pivot URL", style="cyan", no_wrap=False, overflow="fold")

    for platform, url in data.get("lookup_links", {}).items():
        link_table.add_row(platform, f"[underline]{escape(url)}[/underline]")

    console.print(link_table)
    console.print()


def handle_name(full_name: str, output_json: bool):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Compiling real-name correlation dorks for: {full_name}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = generate_name_dorks(full_name)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal menyusun query nama:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    summary_card = Table(box=None, padding=(0, 1), show_header=False)
    summary_card.add_column("Key", style=MUTED_COLOR, width=22)
    summary_card.add_column("Value", style="white")
    summary_card.add_row("Target Name", f"[bold white]{data['name']}[/bold white]")
    summary_card.add_row("Total Target Queries", f"[bold {MINT}]{data['total_queries']} queries disiapkan[/bold {MINT}]")
    summary_card.add_row("Kategori Pencarian", f"{len(data['categories'])} kategori rekognisi")
    console.print(make_card("Real Name Correlation Engine", summary_card))
    console.print()

    flat_queries = []
    global_idx = 1

    for cat_name, queries in data.get("categories", {}).items():
        table = make_table(cat_name)
        table.add_column("No", justify="center", style=f"bold {MINT}", width=4)
        table.add_column("Tujuan Rekognisi", style="bold white", width=28)
        table.add_column("Google Search Query & Direct Link", style="white", no_wrap=False, overflow="fold")

        for q in queries:
            obj_desc = f"{escape(q['title'])}\n[dim]{escape(q['desc'])}[/dim]"
            query_link = f"[bold white]{escape(q['query'])}[/bold white]\n[cyan underline]{escape(q['url'])}[/cyan underline]"
            table.add_row(f"{global_idx:02d}", obj_desc, query_link)
            flat_queries.append(q)
            global_idx += 1

        console.print(table)
        console.print()

    return flat_queries


def handle_profile(username: str, output_json: bool):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Grabbing deep profile metadata for @{username}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = grab_profile_metadata(username)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal mengambil metadata profil:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    gh = data.get("github", {})
    if gh.get("found"):
        gh_table = Table(box=None, padding=(0, 1), show_header=False)
        gh_table.add_column("Key", style=MUTED_COLOR, width=20)
        gh_table.add_column("Value", style="white")

        gh_table.add_row("Real Name", f"[bold white]{escape(gh.get('name'))}[/bold white]")
        gh_table.add_row("Bio", escape(gh.get("bio")))
        gh_table.add_row("Company", escape(gh.get("company")))
        gh_table.add_row("Location", escape(gh.get("location")))
        gh_table.add_row("Public Repos", str(gh.get("public_repos")))
        gh_table.add_row("Followers", str(gh.get("followers")))
        gh_table.add_row("Account Created", escape(gh.get("created_date")))
        gh_table.add_row("Profile URL", f"[underline]{escape(gh.get('profile_url'))}[/underline]")

        console.print(make_card("GitHub Developer Profile", gh_table))
        console.print()

    rd = data.get("reddit", {})
    if rd.get("found"):
        rd_table = Table(box=None, padding=(0, 1), show_header=False)
        rd_table.add_column("Key", style=MUTED_COLOR, width=20)
        rd_table.add_column("Value", style="white")

        rd_table.add_row("Subreddit / Name", f"[bold white]{escape(rd.get('display_name'))}[/bold white]")
        rd_table.add_row("Bio", escape(rd.get("bio")))
        rd_table.add_row("Total Karma", f"[bold {MINT}]{rd.get('total_karma'):,}[/bold {MINT}]")
        rd_table.add_row("Created Date", escape(rd.get("created_date")))
        rd_table.add_row("Verified Email", f"[{MINT}]YA[/{MINT}]" if rd.get("verified_email") else "[dim]TIDAK[/dim]")
        rd_table.add_row("Profile URL", f"[underline]{escape(rd.get('profile_url'))}[/underline]")

        console.print(make_card("Reddit Community Profile", rd_table))
        console.print()

    tg = data.get("telegram", {})
    if tg.get("found"):
        tg_table = Table(box=None, padding=(0, 1), show_header=False)
        tg_table.add_column("Key", style=MUTED_COLOR, width=20)
        tg_table.add_column("Value", style="white")

        tg_table.add_row("Display Name", f"[bold white]{escape(tg.get('name'))}[/bold white]")
        tg_table.add_row("Bio / Description", escape(tg.get("bio")))
        tg_table.add_row("Telegram Link", f"[underline]{escape(tg.get('profile_url'))}[/underline]")

        console.print(make_card("Telegram Public Profile", tg_table))
        console.print()

    tt = data.get("tiktok", {})
    if tt.get("found"):
        tt_table = Table(box=None, padding=(0, 1), show_header=False)
        tt_table.add_column("Key", style=MUTED_COLOR, width=22)
        tt_table.add_column("Value", style="white")

        tt_table.add_row("Display Name / Nickname", f"[bold white]{escape(tt.get('nickname'))}[/bold white]")
        tt_table.add_row("Numeric User ID", f"[bold {MINT}]{escape(tt.get('user_id'))}[/bold {MINT}]")
        tt_table.add_row("SecUid", escape(str(tt.get("sec_uid", ""))[:42] + "..."))
        tt_table.add_row("Bio / Signature", escape(tt.get("bio", "")))
        tt_table.add_row("Followers / Following", f"{tt.get('followers', 0):,} Followers | {tt.get('following', 0):,} Following")
        tt_table.add_row("Likes / Video Count", f"{tt.get('likes', 0):,} Likes | {tt.get('video_count', 0):,} Videos")
        tt_table.add_row("Profile URL", f"[underline]{escape(tt.get('profile_url'))}[/underline]")

        console.print(make_card("TikTok Account Intelligence", tt_table))
        console.print()

        dorks = tt.get("pivot_dorks", {})
        if dorks:
            d_table = make_table("TikTok Investigation Dorks & Archives")
            d_table.add_column("Target Portal", style="bold white", width=28)
            d_table.add_column("Pivot Link / Dork", style="cyan", no_wrap=False, overflow="fold")
            for name, url in dorks.items():
                d_table.add_row(name, f"[underline]{escape(url)}[/underline]")
            console.print(d_table)
            console.print()


def handle_full(username: str, email: str | None, phone: str | None, export_html: str | None = None):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Conducting full identity intelligence on target...[/bold white]", spinner="dots", spinner_style=MINT):
        user_data = scout_username_all(username)
        meta_data = grab_profile_metadata(username)
        email_data = scout_email_identity(email) if email else {}
        phone_data = scout_phone_number(phone) if phone else {}

    render_banner()

    target_name = (
        meta_data.get("github", {}).get("name") or
        meta_data.get("tiktok", {}).get("nickname") or
        meta_data.get("telegram", {}).get("name") or
        username
    )
    avatar_url = (
        meta_data.get("github", {}).get("avatar_url") or
        meta_data.get("tiktok", {}).get("avatar_url") or
        meta_data.get("telegram", {}).get("avatar_url") or
        email_data.get("gravatar", {}).get("avatar_url")
    )

    console.print(Panel(
        f"[bold white]Target:[/bold white] [bold {MINT}]@{username}[/bold {MINT}] | "
        f"[bold white]Nama:[/bold white] {target_name} | "
        f"[bold white]Akun Ditemukan:[/bold white] [bold {MINT}]{user_data.get('total_found', 0)} platform[/bold {MINT}]",
        box=box.ROUNDED,
        border_style=MINT,
        padding=(0, 1)
    ))
    console.print()

    # Quick summary of platforms found
    if user_data.get("profiles"):
        p_table = make_table("Top Discovered Profiles")
        p_table.add_column("No", justify="center", style=f"bold {MINT}", width=4)
        p_table.add_column("Platform", style="bold white", width=22)
        p_table.add_column("Profile URL", style="cyan", no_wrap=False, overflow="fold")

        for idx, p in enumerate(user_data["profiles"][:15], 1):
            p_table.add_row(str(idx), escape(p["platform"]), f"[underline]{escape(p['url'])}[/underline]")

        if len(user_data["profiles"]) > 15:
            p_table.add_row("...", "...", f"[dim]...plus {len(user_data['profiles']) - 15} more profiles[/dim]")

        console.print(p_table)
        console.print()

    if email_data and email_data.get("success"):
        br = email_data.get("breaches", {})
        console.print(f"[{MINT}]✓[/{MINT}] [bold white]Email Status:[/bold white] {email} ({br.get('count', 0)} insiden kebocoran data terdeteksi)")

    if phone_data and phone_data.get("success"):
        console.print(f"[{MINT}]✓[/{MINT}] [bold white]Phone Carrier:[/bold white] {phone_data.get('e164')} -> {phone_data.get('carrier')}")

    console.print()

    if export_html:
        target_payload = {
            "name": target_name,
            "username": username,
            "avatar_url": avatar_url,
            "bio": meta_data.get("github", {}).get("bio") or meta_data.get("telegram", {}).get("bio"),
            "location": meta_data.get("github", {}).get("location"),
            "company": meta_data.get("github", {}).get("company"),
            "profiles": user_data.get("profiles", []),
            "email_data": email_data,
            "phone_data": phone_data
        }
        report_file = generate_person_dossier_html(target_payload, export_html)
        console.print(f"[bold {MINT}]✓[/bold {MINT}] HTML Person Dossier berhasil dibuat: [underline]{report_file}[/underline]\n")
        try:
            webbrowser.open(os.path.abspath(report_file))
        except Exception:
            pass



def handle_snowflake(snowflake_id: str, platform: str = "auto", output_json: bool = False):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Decoding Snowflake ID {snowflake_id}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = decode_snowflake_id(snowflake_id, platform)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal mendekode Snowflake ID:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    card = Table(box=None, padding=(0, 1), show_header=False)
    card.add_column("Key", style=MUTED_COLOR, width=24)
    card.add_column("Value", style="white")

    card.add_row("Snowflake ID", f"[bold white]{data['snowflake_id']}[/bold white]")
    card.add_row("Platform Source", f"[bold {MINT}]{data['platform']}[/bold {MINT}] ({data['epoch']})")
    card.add_row("Exact Timestamp (UTC)", f"[bold white]{data['created_utc']}[/bold white]")
    card.add_row("Exact Timestamp (WIB)", f"[bold {MINT}]{data['created_wib']}[/bold {MINT}]")
    card.add_row("Worker / Machine ID", str(data['internal_worker_id']))
    card.add_row("Process ID", str(data['internal_process_id']))
    card.add_row("Sequence Counter", str(data['sequence']))

    console.print(make_card("Snowflake ID Chronolocation & Timestamp", card))
    console.print()

    pivot_links = data.get("pivot_links", {})
    if pivot_links:
        table = make_table("Investigation Archive & Pivot Resources")
        table.add_column("Resource Pivot", style="bold white", width=34)
        table.add_column("Pivot URL / Query", style="cyan", no_wrap=False, overflow="fold")

        for name, url in pivot_links.items():
            table.add_row(name, f"[underline]{escape(url)}[/underline]")

        console.print(table)
        console.print()


def handle_exif(image_path: str, output_json: bool = False):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Inspecting image forensic metadata: {image_path}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = analyze_image_forensics(image_path)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal menganalisis gambar:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    card = Table(box=None, padding=(0, 1), show_header=False)
    card.add_column("Key", style=MUTED_COLOR, width=22)
    card.add_column("Value", style="white")

    card.add_row("Nama Berkas", escape(data['file_name']))
    card.add_row("Ukuran & Resolusi", f"{data['file_size_kb']} KB ({data['dimensions']}, {data['format']})")
    card.add_row("Perangkat Kamera", f"[bold white]{escape(data['device_make'])} {escape(data['device_model'])}[/bold white]")
    card.add_row("Lensa / Optik", escape(data['lens_model']))
    card.add_row("Waktu Pengambilan", f"[bold {MINT}]{escape(data['date_taken'])}[/bold {MINT}]")
    card.add_row("Perangkat Lunak", escape(data['software']))

    console.print(make_card("Image Hardware & Capture Metadata", card))
    console.print()

    gps = data.get("gps", {})
    if gps.get("has_gps"):
        gps_table = Table(box=None, padding=(0, 1), show_header=False)
        gps_table.add_column("Key", style=MUTED_COLOR, width=22)
        gps_table.add_column("Value", style="white")

        gps_table.add_row("Koordinat Lintang (Lat)", f"[bold {MINT}]{gps.get('latitude')}[/bold {MINT}]")
        gps_table.add_row("Koordinat Bujur (Lon)", f"[bold {MINT}]{gps.get('longitude')}[/bold {MINT}]")
        if gps.get("altitude_meters") is not None:
            gps_table.add_row("Ketinggian (Altitude)", f"{gps.get('altitude_meters')} meter")

        console.print(make_card("GPS Geolocation Coordinates Found", gps_table))
        console.print()

        geo_links = gps.get("geo_links", {})
        if geo_links:
            g_table = make_table("Geolocation Mapping & Chronolocation Pivots")
            g_table.add_column("Mapping Engine", style="bold white", width=30)
            g_table.add_column("Direct Pivot URL", style="cyan", no_wrap=False, overflow="fold")
            for name, url in geo_links.items():
                g_table.add_row(name, f"[underline]{escape(url)}[/underline]")
            console.print(g_table)
            console.print()
    else:
        console.print(f"[{AMBER}]Tidak ditemukan koordinat GPS pada berkas gambar ini.[/{AMBER}]\n")

    tamper = data.get("tamper_assessment", {})
    t_color = RED if tamper.get("is_flagged") else MINT
    t_status = "PERINGATAN: TERDETEKSI JEJAK MODIFIKASI" if tamper.get("is_flagged") else "BERSIH / TIDAK TERINDIKASI EDITOR"

    t_card = Table(box=None, padding=(0, 1), show_header=False)
    t_card.add_column("Key", style=MUTED_COLOR, width=22)
    t_card.add_column("Value", style="white")
    t_card.add_row("Status Forensik", f"[bold {t_color}]{t_status}[/bold {t_color}]")
    t_card.add_row("Catatan Kompresi", escape(tamper.get("notes", "")))
    for flag in tamper.get("flags", []):
        t_card.add_row("Peringatan", f"[bold {RED}]{escape(flag)}[/bold {RED}]")

    console.print(make_card("Forensic Integrity & Tamper Audit", t_card))
    console.print()


def handle_immutable(target_id: str, platform: str, output_json: bool = False):
    with console.status(f"[bold {MINT}]✓[/bold {MINT}] [bold white]Resolving immutable ID pivots for {target_id}...[/bold white]", spinner="dots", spinner_style=MINT):
        data = generate_immutable_pivots(target_id, platform)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal memproses immutable ID:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    card = Table(box=None, padding=(0, 1), show_header=False)
    card.add_column("Key", style=MUTED_COLOR, width=22)
    card.add_column("Value", style="white")
    card.add_row("Target ID", f"[bold white]{data['target_id']}[/bold white]")
    card.add_row("Platform Source", f"[bold {MINT}]{data['platform']}[/bold {MINT}]")
    card.add_row("Deskripsi Forensik", escape(data['description']))

    console.print(make_card("Immutable Identifier Profile", card))
    console.print()

    pivots = data.get("pivots", {})
    if pivots:
        t = make_table("Immutable Verification & Footprint Pivots")
        t.add_column("Target Portal", style="bold white", width=34)
        t.add_column("Direct Pivot URL", style="cyan", no_wrap=False, overflow="fold")
        for name, url in pivots.items():
            t.add_row(name, f"[underline]{escape(url)}[/underline]")
        console.print(t)
        console.print()


def handle_intersect(list_a: list[str], list_b: list[str], label_a: str = "Akun A", label_b: str = "Akun B", output_json: bool = False):
    data = analyze_social_graph_overlap(list_a, list_b, label_a, label_b)

    if output_json:
        console.print_json(data=data)
        return

    render_banner()

    if not data.get("success"):
        console.print(Panel(
            f"[bold {RED}]Gagal menganalisis irisan lingkaran:[/bold {RED}] {escape(str(data.get('error', 'Error tidak diketahui')))}",
            box=box.ROUNDED,
            border_style=RED,
            padding=(0, 1)
        ))
        return

    card = Table(box=None, padding=(0, 1), show_header=False)
    card.add_column("Key", style=MUTED_COLOR, width=24)
    card.add_column("Value", style="white")

    card.add_row(f"Total {label_a}", f"{data['count_a']} akun")
    card.add_row(f"Total {label_b}", f"{data['count_b']} akun")
    card.add_row("Koneksi Bersama (Irisan)", f"[bold {MINT}]{data['shared_count']} akun mutual[/bold {MINT}]")
    card.add_row("Indeks Kemiripan (Jaccard)", f"[bold white]{data['similarity_index']}%[/bold white]")
    r_color = RED if data['correlation_level'] == "SANGAT TINGGI" else (AMBER if data['correlation_level'] == "SEDANG" else MINT)
    card.add_row("Tingkat Korelasi", f"[bold {r_color}]{data['correlation_level']}[/bold {r_color}]")
    card.add_row("Penilaian Intelijen", escape(data['assessment']))

    console.print(make_card("Social Graph & Sock-Puppet Intersect Analysis", card))
    console.print()

    shared = data.get("shared_accounts", [])
    if shared:
        table = make_table(f"Akun Bersama / Mutual Connections ({len(shared)})")
        table.add_column("No", justify="center", style=f"bold {MINT}", width=4)
        table.add_column("Mutual Username", style="bold white", width=28)
        table.add_column("Investigative Note", style=MUTED_COLOR)

        for idx, u in enumerate(shared, 1):
            table.add_row(str(idx), f"@{escape(u)}", "Akun mutual yang terhubung ke kedua profil target")

        console.print(table)
        console.print()
    else:
        console.print(f"[{AMBER}]Tidak ditemukan akun mutual yang sama di antara kedua daftar.[/{AMBER}]\n")


# -------------------------------------------------------------
# Interactive Menu
# -------------------------------------------------------------

def interactive_menu():
    while True:
        try:
            clear_screen()
            render_banner()

            menu_table = Table(
                title=None,
                box=box.SIMPLE_HEAD,
                border_style=BORDER_DARK,
                padding=(0, 1)
            )
            menu_table.add_column("No", justify="center", style=f"bold {MINT}", width=4)
            menu_table.add_column("Investigation Module", style="bold white", width=28)
            menu_table.add_column("Intelligence Scope & Capabilities", style=MUTED_COLOR, width=44)
            menu_table.add_column("Status", justify="right", width=10)

            modules_data = [
                ("01", "Full Person Intelligence", "Username + Email + Phone combo scanning", "ONLINE"),
                ("02", "Cross-Platform Username", "Scan alias target across 50+ services", "ONLINE"),
                ("03", "Email Breach & Gravatar", "Eksposur password, leak Xposed, avatar", "ONLINE"),
                ("04", "Phone Number & Carrier", "Operator seluler, E.164, chat WA/Telegram", "ONLINE"),
                ("05", "Real Name Dorking Engine", "PDDikti, CV, Scholar, LinkedIn, Putusan MA", "ONLINE"),
                ("06", "Profile Metadata Grabber", "Deep bio, avatar, karma GitHub & Reddit", "ONLINE"),
                ("07", "Generate HTML Dossier", "Export laporan lengkap profil + auto browser", "STANDBY"),
                ("08", "Snowflake Timestamp Decoder", "Milidetik tweet/Discord & archive dork", "ONLINE"),
                ("09", "Image & EXIF Forensics GPS", "Kamera, lokasi GPS Google Maps, SunCalc", "ONLINE"),
                ("10", "Immutable ID Pivots", "Google Maps Contributor, IG PK, Telegram ID", "ONLINE"),
                ("11", "Social Graph Circle Intersect", "Deteksi akun alter/sock-puppet lewat mutual", "ONLINE"),
                ("00", "Exit Console", "Tutup sesi investigasi", "EXIT"),
            ]

            for no, name, desc, status in modules_data:
                st_style = f"bold {MINT}" if status == "ONLINE" else ("bold white" if status == "STANDBY" else "dim")
                menu_table.add_row(no, name, desc, f"[{st_style}]{status}[/{st_style}]")

            console.print(menu_table)
            console.print()

            raw_choice = ask_input("Select module [1-11, 0 to exit]: ").lower()

            if raw_choice in ["0", "00", "q", "exit", "quit", "keluar"]:
                console.print(f"\n[{MINT}]✓[/{MINT}] [dim]Menutup PeopleScout. Sampai jumpa![/dim]")
                sys.exit(0)

            if not raw_choice:
                continue

            choice_clean = raw_choice.lstrip("0") if raw_choice != "0" else "0"

            if choice_clean not in [str(i) for i in range(1, 12)]:
                console.print(f"\n[{AMBER}]Pilihan tidak valid. Masukkan angka antara 0 sampai 11.[/{AMBER}]")
                import time
                time.sleep(1.2)
                continue

            clear_screen()
            render_banner()

            if choice_clean == "1":
                console.print(f"[bold white]─── [01] Full Person Intelligence Dossier ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                username = ask_input("Masukkan username target (contoh: torvalds): ")
                if username and username.lower() not in ["b", "back", "0"]:
                    email = ask_input("Masukkan email target (opsional, tekan Enter untuk lewati): ")
                    phone = ask_input("Masukkan nomor telepon (opsional, tekan Enter untuk lewati): ")
                    html_name = f"dossier_person_{username}.html"
                    console.print()
                    try:
                        handle_full(username, email or None, phone or None, export_html=html_name)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Full Recon Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "2":
                console.print(f"[bold white]─── [02] Cross-Platform Username Scout ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                username = ask_input("Masukkan username target (contoh: torvalds): ")
                if username and username.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_username(username, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Username Scout Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "3":
                console.print(f"[bold white]─── [03] Email Identity & Breach Audit ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                email = ask_input("Masukkan email target (contoh: user@gmail.com): ")
                if email and email.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_email(email, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Email Scout Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "4":
                console.print(f"[bold white]─── [04] Phone Number & Carrier Intelligence ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                phone = ask_input("Masukkan nomor telepon (contoh: 081234567890): ")
                if phone and phone.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_phone(phone, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Phone Scout Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "5":
                console.print(f"[bold white]─── [05] Real Name Correlation Dorks ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                name = ask_input("Masukkan nama lengkap target (contoh: Budi Santoso): ")
                if name and name.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        flat_dorks = handle_name(name, output_json=False)
                        if flat_dorks:
                            while True:
                                sub = ask_input(f"Buka dork di browser [1-{len(flat_dorks)}, atau Enter untuk selesai]: ")
                                if not sub or sub.lower() in ["b", "back", "0", "exit"]:
                                    break
                                try:
                                    num = int(sub)
                                    if 1 <= num <= len(flat_dorks):
                                        selected = flat_dorks[num - 1]
                                        console.print(f"[{MINT}]✓[/{MINT}] Membuka pencarian #{num:02d} ([bold white]{selected['title']}[/bold white]) di browser...")
                                        webbrowser.open(selected["url"])
                                    else:
                                        console.print(f"[{AMBER}]Nomor tidak ada.[/{AMBER}]")
                                except ValueError:
                                    console.print(f"[{AMBER}]Input tidak valid.[/{AMBER}]")
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Name Dork Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "6":
                console.print(f"[bold white]─── [06] Profile Metadata Grabber ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                username = ask_input("Masukkan username target (contoh: torvalds): ")
                if username and username.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_profile(username, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Profile Grabber Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "7":
                console.print(f"[bold white]─── [07] Generate Full HTML Person Dossier ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                username = ask_input("Masukkan username target (contoh: torvalds): ")
                if username and username.lower() not in ["b", "back", "0"]:
                    html_file = f"dossier_person_{username}.html"
                    console.print()
                    try:
                        handle_full(username, None, None, export_html=html_file)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Dossier Generation Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "8":
                console.print(f"[bold white]─── [08] Snowflake Timestamp & Chronolocation Decoder ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                snow_id = ask_input("Masukkan Snowflake ID (contoh: 1630000000000000000): ")
                if snow_id and snow_id.lower() not in ["b", "back", "0"]:
                    plat = ask_input("Platform [twitter/discord/auto, default: auto]: ") or "auto"
                    console.print()
                    try:
                        handle_snowflake(snow_id, plat, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Snowflake Decoder Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "9":
                console.print(f"[bold white]─── [09] Image & EXIF Forensic Geolocation Grabber ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                img_path = ask_input("Masukkan path berkas gambar (contoh: bukti_foto.jpg): ")
                if img_path and img_path.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_exif(img_path, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]EXIF Forensics Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "10":
                console.print(f"[bold white]─── [10] Platform Immutable Identifier Pivots ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                console.print(f"Pilih platform: [1] Google Contributor/GAIA ID  [2] Instagram PK ID  [3] Telegram Peer ID")
                plat_choice = ask_input("Pilihan [1/2/3]: ")
                plat_map = {"1": "google", "2": "instagram", "3": "telegram"}
                chosen_plat = plat_map.get(plat_choice, "google")
                target_id = ask_input(f"Masukkan ID numerik {chosen_plat.capitalize()}: ")
                if target_id and target_id.lower() not in ["b", "back", "0"]:
                    console.print()
                    try:
                        handle_immutable(target_id, chosen_plat, output_json=False)
                    except Exception as err:
                        console.print(f"\n[bold {RED}]Immutable Pivot Error:[/bold {RED}] {err}")
                    console.print()
                    ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

            elif choice_clean == "11":
                console.print(f"[bold white]─── [11] Social Graph & Circle Intersect Analysis ───[/bold white]")
                console.print(f"[dim]Ketik 'b' atau tekan Enter untuk kembali ke menu utama[/dim]\n")
                console.print(f"[dim]Masukkan username dipisahkan dengan koma atau spasi[/dim]\n")
                raw_a = ask_input("Daftar follower/following Akun A: ")
                if raw_a and raw_a.lower() not in ["b", "back", "0"]:
                    raw_b = ask_input("Daftar follower/following Akun B (Akun Terduga Alter): ")
                    if raw_b and raw_b.lower() not in ["b", "back", "0"]:
                        import re
                        list_a = [x for x in re.split(r"[\s,]+", raw_a) if x]
                        list_b = [x for x in re.split(r"[\s,]+", raw_b) if x]
                        console.print()
                        try:
                            handle_intersect(list_a, list_b, label_a="Akun A", label_b="Akun B", output_json=False)
                        except Exception as err:
                            console.print(f"\n[bold {RED}]Social Graph Error:[/bold {RED}] {err}")
                        console.print()
                        ask_input("[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n\n[{MINT}]✓[/{MINT}] [dim]Menutup PeopleScout. Sampai jumpa![/dim]")
            sys.exit(0)
        except Exception as global_err:
            console.print(f"\n[bold {RED}]Runtime Error:[/bold {RED}] {global_err}")
            ask_input("\n[dim]Tekan Enter untuk kembali ke menu utama...[/dim]")


# -------------------------------------------------------------
# Main CLI Entrypoint
# -------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="PeopleScout v2.0 - Deep Identity, Username & People Intelligence Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python people_scout.py user torvalds
  python people_scout.py email target@gmail.com
  python people_scout.py phone 081234567890
  python people_scout.py name "Budi Santoso"
  python people_scout.py profile torvalds
  python people_scout.py full torvalds --export-html dossier_torvalds.html
        """
    )
    parser.add_argument("--json", action="store_true", help="Output raw JSON format")
    parser.add_argument("--export-html", help="Generate and export comprehensive HTML report to specified file")

    subparsers = parser.add_subparsers(dest="command", required=False)

    p_user = subparsers.add_parser("user", help="Scan username identity across 50+ platforms")
    p_user.add_argument("username", help="Target username (e.g. torvalds)")
    p_user.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_email = subparsers.add_parser("email", help="Audit email identity, Gravatar profile, and breach history")
    p_email.add_argument("email", help="Target email address (e.g. user@gmail.com)")
    p_email.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_phone = subparsers.add_parser("phone", help="Phone intelligence, carrier detection, and chat pivots")
    p_phone.add_argument("phone", help="Target phone number (e.g. 081234567890)")
    p_phone.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_name = subparsers.add_parser("name", help="Real name correlation dorks across academic, civil, and social portals")
    p_name.add_argument("full_name", help="Target full name (e.g. 'Budi Santoso')")
    p_name.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_profile = subparsers.add_parser("profile", help="Deep profile metadata grabber (GitHub, Reddit, Telegram)")
    p_profile.add_argument("username", help="Target username (e.g. torvalds)")
    p_profile.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_snow = subparsers.add_parser("snowflake", help="Decode Twitter/Discord Snowflake IDs to exact millisecond creation timestamp")
    p_snow.add_argument("snowflake_id", help="Numeric Snowflake ID")
    p_snow.add_argument("--platform", default="auto", choices=["auto", "twitter", "discord"], help="Target platform (default: auto)")
    p_snow.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_exif = subparsers.add_parser("exif", help="Image & EXIF forensics: GPS location pin, camera model, and tamper detection")
    p_exif.add_argument("image_path", help="Path to local image file (.jpg, .png, etc.)")
    p_exif.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_pivot = subparsers.add_parser("pivot", help="Platform immutable ID pivots (Google GAIA, Instagram PK ID, Telegram Peer ID)")
    p_pivot.add_argument("target_id", help="Numeric account ID")
    p_pivot.add_argument("--platform", choices=["google", "instagram", "telegram"], default="google", help="Platform name")
    p_pivot.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_intersect = subparsers.add_parser("intersect", help="Social graph correlation and sock-puppet follower overlap analysis")
    p_intersect.add_argument("list_a", help="Comma-separated usernames for account A")
    p_intersect.add_argument("list_b", help="Comma-separated usernames for account B")
    p_intersect.add_argument("--label-a", default="Target A", help="Label for account A")
    p_intersect.add_argument("--label-b", default="Target B", help="Label for account B")
    p_intersect.add_argument("--json", action="store_true", help="Output raw JSON format")

    p_full = subparsers.add_parser("full", help="Full automated person intelligence investigation")
    p_full.add_argument("username", help="Target username")
    p_full.add_argument("--email", help="Target email (optional)")
    p_full.add_argument("--phone", help="Target phone (optional)")
    p_full.add_argument("--export-html", help="Export to HTML dossier")

    args = parser.parse_args()

    if not args.command:
        interactive_menu()
        return

    is_json = getattr(args, "json", False) or ("--json" in sys.argv)

    if args.command == "user":
        handle_username(args.username, is_json)
    elif args.command == "email":
        handle_email(args.email, is_json)
    elif args.command == "phone":
        handle_phone(args.phone, is_json)
    elif args.command == "name":
        handle_name(args.full_name, is_json)
    elif args.command == "profile":
        handle_profile(args.username, is_json)
    elif args.command == "snowflake":
        handle_snowflake(args.snowflake_id, getattr(args, "platform", "auto"), is_json)
    elif args.command == "exif":
        handle_exif(args.image_path, is_json)
    elif args.command == "pivot":
        handle_immutable(args.target_id, getattr(args, "platform", "google"), is_json)
    elif args.command == "intersect":
        import re
        list_a = [x for x in re.split(r"[\s,]+", args.list_a) if x]
        list_b = [x for x in re.split(r"[\s,]+", args.list_b) if x]
        handle_intersect(list_a, list_b, getattr(args, "label_a", "Target A"), getattr(args, "label_b", "Target B"), is_json)
    elif args.command == "full":
        handle_full(args.username, getattr(args, "email", None), getattr(args, "phone", None), getattr(args, "export_html", None))


if __name__ == "__main__":
    main()
