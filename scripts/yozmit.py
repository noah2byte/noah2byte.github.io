import requests
import json
import time
import re
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser
import urllib.robotparser as robotparser

# -----------------------------
# 설정
# -----------------------------
SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap-news.xml"
BASE_URL = "https://yozm.wishket.com"

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")

output_dir = Path("_weekly")
cache_dir = Path("_cache")

output_dir.mkdir(parents=True, exist_ok=True)
cache_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"yozmit-{today_str}.md"
cache_file = cache_dir / "yozmit-cache.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------------
# robots.txt (안전)
# -----------------------------
rp = robotparser.RobotFileParser()
rp.set_url(f"{BASE_URL}/robots.txt")

try:
    rp.read()
except:
    print("[WARN] robots.txt load failed")


def allowed(url: str) -> bool:
    try:
        return rp.can_fetch(headers["User-Agent"], url)
    except:
        return True


# -----------------------------
# 핵심: 제목 정제 (regex 버전)
# -----------------------------
def clean_title(title: str) -> str:
    if not title:
        return "Untitled"

    title = title.strip()

    # " | 요즘IT" 정확히 제거 (공백 포함)
    title = re.sub(r"\s\|\s요즘IT\s*$", "", title)

    return title.strip()


# -----------------------------
# cache
# -----------------------------
def load_cache():
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    return []


def save_cache(data):
    cache_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


# -----------------------------
# sitemap fetch
# -----------------------------
def fetch_sitemap():
    try:
        r = requests.get(SITEMAP_URL, headers=headers, timeout=30)
        if r.status_code == 200:
            return r
    except Exception as e:
        print("[ERROR] sitemap request failed:", e)
    return None


# -----------------------------
# 1. sitemap
# -----------------------------
response = fetch_sitemap()
urls = []

# -----------------------------
# 2. fallback
# -----------------------------
if not response:
    print("[WARN] sitemap failed → cache fallback")

    urls = load_cache()

    if not urls:
        print("[FATAL] no cache data")
        exit(1)

else:
    print("[INFO] sitemap OK")

    soup = BeautifulSoup(response.content, "lxml-xml")
    items = soup.find_all("url")

    week_ago = today.date() - timedelta(days=7)

    for item in items:
        loc = item.find("loc")
        lastmod = item.find("lastmod")

        if not loc or not lastmod:
            continue

        url = loc.text.strip()

        if not allowed(url):
            continue

        try:
            modified = parser.parse(lastmod.text.strip()).date()

            if modified >= week_ago:
                urls.append(url)

        except:
            continue

    save_cache(urls)

print(f"[INFO] urls: {len(urls)}")

# -----------------------------
# 3. 안전 종료
# -----------------------------
if not urls:
    print("[WARN] empty result → skip")
    exit(0)

# -----------------------------
# 4. MD 생성
# -----------------------------
with open(output_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: page\n")
    f.write(f"title: 요즘IT Weekly - {today_str}\n")
    f.write(f"permalink: /weekly/yozmit/{today_str}/\n")
    f.write("---\n\n")

    f.write(f"# 요즘IT Weekly - {today_str}\n\n")
    f.write("## Articles\n\n")

    for url in urls:
        try:
            time.sleep(1)

            r = requests.get(url, headers=headers, timeout=30)
            page = BeautifulSoup(r.text, "html.parser")

            title = None

            # -----------------------------
            # title 후보 수집
            # -----------------------------
            meta = page.find("meta", property="og:title")

            if meta and meta.get("content"):
                title = meta["content"]
            elif page.title:
                title = page.title.get_text(strip=True)
            else:
                title = "Untitled"

            # -----------------------------
            # 핵심: 무조건 마지막 1회 정제
            # -----------------------------
            title = clean_title(title)

            print("[OK]", title)
            f.write(f"- [{title}]({url})\n")

        except Exception as e:
            print("[ERROR]", url, e)

print(f"[DONE] created: {output_file}")
