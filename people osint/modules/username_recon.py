import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

PLATFORMS = {
    # Developer & Code
    "GitHub": {
        "category": "Developer & Code",
        "url": "https://github.com/{}",
        "check": "status_code"
    },
    "GitLab": {
        "category": "Developer & Code",
        "url": "https://gitlab.com/{}",
        "check": "status_code"
    },
    "Bitbucket": {
        "category": "Developer & Code",
        "url": "https://bitbucket.org/{}/",
        "check": "status_code"
    },
    "DockerHub": {
        "category": "Developer & Code",
        "url": "https://hub.docker.com/u/{}/",
        "check": "status_code"
    },
    "Dev.to": {
        "category": "Developer & Code",
        "url": "https://dev.to/{}",
        "check": "status_code"
    },
    "HuggingFace": {
        "category": "Developer & Code",
        "url": "https://huggingface.co/{}",
        "check": "status_code"
    },
    "Kaggle": {
        "category": "Developer & Code",
        "url": "https://www.kaggle.com/{}",
        "check": "status_code"
    },
    "PyPI": {
        "category": "Developer & Code",
        "url": "https://pypi.org/user/{}/",
        "check": "status_code"
    },
    "NPM": {
        "category": "Developer & Code",
        "url": "https://www.npmjs.com/~{}",
        "check": "status_code"
    },
    "Hashnode": {
        "category": "Developer & Code",
        "url": "https://hashnode.com/@{}",
        "check": "status_code"
    },
    "Replit": {
        "category": "Developer & Code",
        "url": "https://replit.com/@{}",
        "check": "status_code"
    },
    "CodePen": {
        "category": "Developer & Code",
        "url": "https://codepen.io/{}",
        "check": "status_code"
    },
    "LeetCode": {
        "category": "Developer & Code",
        "url": "https://leetcode.com/u/{}/",
        "check": "status_code"
    },
    "Codeforces": {
        "category": "Developer & Code",
        "url": "https://codeforces.com/profile/{}",
        "check": "status_code"
    },
    "Packagist": {
        "category": "Developer & Code",
        "url": "https://packagist.org/users/{}/",
        "check": "status_code"
    },
    "Crates.io": {
        "category": "Developer & Code",
        "url": "https://crates.io/users/{}",
        "check": "status_code"
    },

    # Social Media & Communities
    "Reddit": {
        "category": "Social Media & Community",
        "url": "https://www.reddit.com/user/{}/about.json",
        "profile_url": "https://www.reddit.com/user/{}/",
        "check": "reddit_json"
    },
    "Twitter / X": {
        "category": "Social Media & Community",
        "url": "https://x.com/{}",
        "check": "status_code"
    },
    "Instagram": {
        "category": "Social Media & Community",
        "url": "https://www.instagram.com/{}/",
        "check": "status_code"
    },
    "TikTok": {
        "category": "Social Media & Community",
        "url": "https://www.tiktok.com/@{}",
        "check": "status_code"
    },
    "Threads": {
        "category": "Social Media & Community",
        "url": "https://www.threads.net/@{}",
        "check": "status_code"
    },
    "Pinterest": {
        "category": "Social Media & Community",
        "url": "https://www.pinterest.com/{}/",
        "check": "status_code"
    },
    "Tumblr": {
        "category": "Social Media & Community",
        "url": "https://{}.tumblr.com",
        "check": "status_code"
    },
    "Medium": {
        "category": "Social Media & Community",
        "url": "https://medium.com/@{}",
        "check": "status_code"
    },
    "Substack": {
        "category": "Social Media & Community",
        "url": "https://{}.substack.com",
        "check": "status_code"
    },
    "Quora": {
        "category": "Social Media & Community",
        "url": "https://www.quora.com/profile/{}",
        "check": "status_code"
    },
    "Mastodon Social": {
        "category": "Social Media & Community",
        "url": "https://mastodon.social/@{}",
        "check": "status_code"
    },
    "Bluesky": {
        "category": "Social Media & Community",
        "url": "https://bsky.app/profile/{}.bsky.social",
        "check": "status_code"
    },
    "Disqus": {
        "category": "Social Media & Community",
        "url": "https://disqus.com/by/{}/",
        "check": "status_code"
    },
    "HackerNews": {
        "category": "Social Media & Community",
        "url": "https://news.ycombinator.com/user?id={}",
        "check": "hackernews"
    },

    # Gaming & Virtual
    "Steam": {
        "category": "Gaming & Virtual",
        "url": "https://steamcommunity.com/id/{}",
        "check": "steam"
    },
    "Chess.com": {
        "category": "Gaming & Virtual",
        "url": "https://api.chess.com/pub/player/{}",
        "profile_url": "https://www.chess.com/member/{}",
        "check": "status_code"
    },
    "Lichess": {
        "category": "Gaming & Virtual",
        "url": "https://lichess.org/@/{}",
        "check": "status_code"
    },
    "Roblox": {
        "category": "Gaming & Virtual",
        "url": "https://www.roblox.com/user.aspx?username={}",
        "check": "status_code"
    },
    "Twitch": {
        "category": "Gaming & Virtual",
        "url": "https://www.twitch.tv/{}",
        "check": "status_code"
    },
    "Speedrun.com": {
        "category": "Gaming & Virtual",
        "url": "https://www.speedrun.com/user/{}",
        "check": "status_code"
    },
    "osu!": {
        "category": "Gaming & Virtual",
        "url": "https://osu.ppy.sh/users/{}",
        "check": "status_code"
    },

    # Creative, Design & Music
    "SoundCloud": {
        "category": "Creative, Design & Audio",
        "url": "https://soundcloud.com/{}",
        "check": "status_code"
    },
    "Spotify": {
        "category": "Creative, Design & Audio",
        "url": "https://open.spotify.com/user/{}",
        "check": "status_code"
    },
    "Behance": {
        "category": "Creative, Design & Audio",
        "url": "https://www.behance.net/{}",
        "check": "status_code"
    },
    "Dribbble": {
        "category": "Creative, Design & Audio",
        "url": "https://dribbble.com/{}",
        "check": "status_code"
    },
    "ArtStation": {
        "category": "Creative, Design & Audio",
        "url": "https://www.artstation.com/{}",
        "check": "status_code"
    },
    "DeviantArt": {
        "category": "Creative, Design & Audio",
        "url": "https://www.deviantart.com/{}",
        "check": "status_code"
    },
    "500px": {
        "category": "Creative, Design & Audio",
        "url": "https://500px.com/p/{}",
        "check": "status_code"
    },
    "Flickr": {
        "category": "Creative, Design & Audio",
        "url": "https://www.flickr.com/people/{}/",
        "check": "status_code"
    },
    "Bandcamp": {
        "category": "Creative, Design & Audio",
        "url": "https://bandcamp.com/{}",
        "check": "status_code"
    },
    "Vimeo": {
        "category": "Creative, Design & Audio",
        "url": "https://vimeo.com/{}",
        "check": "status_code"
    },

    # Identity, Links & Support
    "Telegram": {
        "category": "Identity & Direct Messaging",
        "url": "https://t.me/{}",
        "check": "telegram"
    },
    "Keybase": {
        "category": "Identity & Direct Messaging",
        "url": "https://keybase.io/{}",
        "check": "status_code"
    },
    "Linktree": {
        "category": "Identity & Direct Messaging",
        "url": "https://linktr.ee/{}",
        "check": "status_code"
    },
    "BuyMeACoffee": {
        "category": "Identity & Direct Messaging",
        "url": "https://www.buymeacoffee.com/{}",
        "check": "status_code"
    },
    "Patreon": {
        "category": "Identity & Direct Messaging",
        "url": "https://www.patreon.com/{}",
        "check": "status_code"
    },
    "About.me": {
        "category": "Identity & Direct Messaging",
        "url": "https://about.me/{}",
        "check": "status_code"
    },
    "ProductHunt": {
        "category": "Identity & Direct Messaging",
        "url": "https://www.producthunt.com/@{}",
        "check": "status_code"
    },
    "Gravatar Profile": {
        "category": "Identity & Direct Messaging",
        "url": "https://en.gravatar.com/{}",
        "check": "status_code"
    },
    "Pastebin": {
        "category": "Identity & Direct Messaging",
        "url": "https://pastebin.com/u/{}",
        "check": "status_code"
    }
}


def _probe_single(platform: str, cfg: dict, username: str) -> dict:
    url = cfg["url"].format(username)
    profile_url = cfg.get("profile_url", url).format(username)
    category = cfg.get("category", "General")
    check_type = cfg.get("check", "status_code")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        r = requests.get(url, headers=headers, timeout=6, allow_redirects=True)
        exists = False

        if check_type == "status_code":
            exists = (r.status_code == 200)
        elif check_type == "telegram":
            exists = (r.status_code == 200 and "tgme_page_extra" in r.text and "If you have Telegram" in r.text)
        elif check_type == "steam":
            exists = (r.status_code == 200 and "The specified profile could not be found" not in r.text)
        elif check_type == "hackernews":
            exists = (r.status_code == 200 and "No such user" not in r.text)
        elif check_type == "reddit_json":
            exists = (r.status_code == 200 and "data" in r.text)

        return {
            "platform": platform,
            "category": category,
            "url": profile_url,
            "exists": exists,
            "status_code": r.status_code
        }
    except Exception:
        return {
            "platform": platform,
            "category": category,
            "url": profile_url,
            "exists": False,
            "status_code": 0
        }


def scout_username_all(username: str, max_workers: int = 25) -> dict:
    cleaned = username.strip().lstrip("@")
    if not cleaned:
        return {"success": False, "error": "Username tidak boleh kosong."}

    total_platforms = len(PLATFORMS)
    found_profiles = []
    category_counts = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(_probe_single, plat, cfg, cleaned): plat
            for plat, cfg in PLATFORMS.items()
        }

        for future in as_completed(future_map):
            res = future.result()
            if res["exists"]:
                found_profiles.append(res)
                cat = res["category"]
                category_counts[cat] = category_counts.get(cat, 0) + 1

    # Sort found profiles by platform name
    found_profiles.sort(key=lambda x: (x["category"], x["platform"]))

    return {
        "success": True,
        "username": cleaned,
        "total_probed": total_platforms,
        "total_found": len(found_profiles),
        "category_counts": category_counts,
        "profiles": found_profiles
    }
