import re
import json
import datetime
import urllib.parse
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
}


def grab_profile_metadata(username: str, timeout: int = 8) -> dict:
    cleaned = username.strip().lstrip("@")
    if not cleaned:
        return {"success": False, "error": "Username tidak boleh kosong."}

    github_profile = _fetch_github(cleaned, timeout)
    reddit_profile = _fetch_reddit(cleaned, timeout)
    telegram_profile = _fetch_telegram(cleaned, timeout)
    tiktok_profile = _fetch_tiktok(cleaned, timeout)

    return {
        "success": True,
        "username": cleaned,
        "github": github_profile,
        "reddit": reddit_profile,
        "telegram": telegram_profile,
        "tiktok": tiktok_profile
    }


def _fetch_github(username: str, timeout: int) -> dict:
    url = f"https://api.github.com/users/{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            d = r.json()
            created_raw = d.get("created_at", "")
            created_fmt = created_raw.split("T")[0] if "T" in created_raw else created_raw

            return {
                "found": True,
                "profile_url": d.get("html_url", f"https://github.com/{username}"),
                "name": d.get("name") or "Tidak dicantumkan",
                "bio": d.get("bio") or "Tidak ada bio",
                "company": d.get("company") or "N/A",
                "location": d.get("location") or "N/A",
                "blog": d.get("blog") or "N/A",
                "twitter": d.get("twitter_username") or "N/A",
                "public_repos": d.get("public_repos", 0),
                "followers": d.get("followers", 0),
                "following": d.get("following", 0),
                "created_date": created_fmt,
                "avatar_url": d.get("avatar_url")
            }
    except Exception:
        pass

    return {"found": False}


def _fetch_reddit(username: str, timeout: int) -> dict:
    url = f"https://www.reddit.com/user/{username}/about.json"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            d = r.json().get("data", {})
            if d:
                created_utc = d.get("created_utc", 0)
                created_date = (
                    datetime.datetime.fromtimestamp(created_utc, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                    if created_utc else "N/A"
                )
                raw_icon = d.get("icon_img", "").split("?")[0]

                return {
                    "found": True,
                    "profile_url": f"https://www.reddit.com/user/{username}/",
                    "display_name": d.get("subreddit", {}).get("title") or username,
                    "bio": d.get("subreddit", {}).get("public_description") or "Tidak ada bio",
                    "total_karma": d.get("total_karma", 0),
                    "link_karma": d.get("link_karma", 0),
                    "comment_karma": d.get("comment_karma", 0),
                    "created_date": created_date,
                    "verified_email": d.get("has_verified_email", False),
                    "avatar_url": raw_icon or None
                }
    except Exception:
        pass

    return {"found": False}


def _fetch_telegram(username: str, timeout: int) -> dict:
    url = f"https://t.me/{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200 and "tgme_page_extra" in r.text:
            soup = BeautifulSoup(r.text, "html.parser")
            title_node = soup.find("div", class_="tgme_page_title")
            desc_node = soup.find("div", class_="tgme_page_description")
            img_node = soup.find("img", class_="tgme_page_photo_image")

            title = title_node.get_text().strip() if title_node else username
            desc = desc_node.get_text().strip() if desc_node else "Tidak ada deskripsi bio"
            photo_url = img_node.get("src") if img_node else None

            return {
                "found": True,
                "profile_url": url,
                "name": title,
                "bio": desc,
                "avatar_url": photo_url
            }
    except Exception:
        pass

    return {"found": False}


def _fetch_tiktok(username: str, timeout: int = 10) -> dict:
    url = f"https://www.tiktok.com/@{username}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200:
            m = re.search(r"__UNIVERSAL_DATA_FOR_REHYDRATION__.*?>(.*?)</script>", r.text, re.DOTALL)
            if m:
                d = json.loads(m.group(1))
                scope = d.get("__DEFAULT_SCOPE__", {})
                udetail = scope.get("webapp.user-detail", {})
                uinfo = udetail.get("userInfo", {})
                u = uinfo.get("user", {})
                s = uinfo.get("stats", {})

                if u.get("id"):
                    user_id = str(u.get("id"))
                    sec_uid = u.get("secUid", "N/A")
                    nickname = u.get("nickname") or username
                    bio = u.get("signature") or "Tidak ada bio"
                    avatar_url = u.get("avatarLarger") or u.get("avatarMedium") or u.get("avatarThumb")
                    verified = u.get("verified", False)

                    followers = s.get("followerCount", 0)
                    following = s.get("followingCount", 0)
                    likes = s.get("heartCount", s.get("heart", 0))
                    videos = s.get("videoCount", 0)
                    friends = s.get("friendCount", 0)

                    return {
                        "found": True,
                        "profile_url": url,
                        "user_id": user_id,
                        "sec_uid": sec_uid,
                        "nickname": nickname,
                        "bio": bio,
                        "followers": followers,
                        "following": following,
                        "likes": likes,
                        "video_count": videos,
                        "friend_count": friends,
                        "verified": verified,
                        "avatar_url": avatar_url,
                        "pivot_dorks": {
                            "TikTok Comments Dork": f'https://www.google.com/search?q={urllib.parse.quote(f"site:tiktok.com intext:\"@{username}\"")}',
                            "TikTok Mentions Dork": f'https://www.google.com/search?q={urllib.parse.quote(f"site:tiktok.com \"{username}\"")}',
                            "Archive.today Profil": f"https://archive.today/{url}"
                        }
                    }
    except Exception:
        pass

    return {"found": False}

