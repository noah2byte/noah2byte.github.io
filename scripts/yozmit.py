import requests
import json
import time
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser

SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap-news.xml"

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")

output_dir = Path("_weekly")
cache_dir = Path("_cache")

output_dir.mkdir(parents=True, exist_ok=True)
cache_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"yozmit-{today_str}.md"
cache_file = cache_dir / "yozmit-latest.json"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# -----------------------------
# 1. sitemap fetch (retry)
# -----------------------------
def fetch_sitemap():
    for i in range(3):
        try:
            r = requests.get(SITEMAP_URL, timeout=30, headers=headers)
            if r.status_code == 200:
                return r
            print(f"[WARN] retry {i+1} status={r.status_code}")
            time.sleep(3)
        except Exception as e:
            print("[ERROR] request failed", e)
    return None


# -----------------------------
# 2. cache load/save
# -----------------------------
def load_cache():
    if cache_file.exists():
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_cache(data):
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# 3. fetch sitemap
# -----------------------------
response = fetch_sitemap()

urls = []

# -----------------------------
# 4. fallback logic
# -----------------------------
if not response or response.status_code != 200:
    print("[ERROR] sitemap failed → using cache")

    urls = load_cache()

    if not urls:
        print("[FATAL] no cache available → exit")
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

        try:
            modified = parser.parse(lastmod.text.strip()).date()

            if modified >= week_ago:
                urls.append(loc.text.strip())

        except:
            continue

    # cache 저장
    save_cache(urls)


print(f"[INFO] URLs: {len(urls)}")

# -----------------------------
# 5. 안전장치 (빈 파일 방지)
# -----------------------------
if len(urls) == 0:
    print("[WARN] empty result → abort")
    exit(0)

# -----------------------------
# 6. MD 생성 (원하는 포맷)
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
            html = requests.get(url, timeout=30, headers=headers)
            page = BeautifulSoup(html.text, "html.parser")

            meta = page.find("meta", property="og:title")

            if meta and meta.get("content"):
                title = meta["content"].strip()
            elif page.title:
                title = page.title.get_text(strip=True)
            else:
                title = "Untitled"

            # ⭐ 원하는 Markdown 포맷
            f.write(f"- [{title}]({url})\n")
            print("[OK]", title)

        except Exception as e:
            print("[ERROR URL]", url, e)

print(f"[DONE] created: {output_file}")
