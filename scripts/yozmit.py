import requests
import json
import time
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
cache_file = cache_dir / "links-cache.json"

headers = {
    "User-Agent": "Mozilla/5.0"
}

# -----------------------------
# robots.txt
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
# sitemap
# -----------------------------
def fetch_sitemap():
    try:
        r = requests.get(SITEMAP_URL, headers=headers, timeout=30)
        if r.status_code == 200:
            return r
    except:
        pass
    return None


# -----------------------------
# 카테고리 분류
# -----------------------------
def classify(url: str, title: str = "") -> str:
    text = (url + " " + title).lower()

    if any(k in text for k in ["ai", "gpt", "llm", "prompt", "rag", "agent"]):
        return "AI / LLM"

    if any(k in text for k in ["kubernetes", "docker", "devops", "ci/cd", "terraform"]):
        return "DevOps / Infra"

    if any(k in text for k in ["api", "server", "backend", "database", "architecture"]):
        return "Backend / System"

    if any(k in text for k in ["security", "oauth", "auth", "attack"]):
        return "Security"

    if any(k in text for k in ["ui", "ux", "frontend", "design"]):
        return "Frontend / UX"

    return "General"


# -----------------------------
# 1. sitemap 수집
# -----------------------------
response = fetch_sitemap()
urls = []

if not response:
    print("[WARN] sitemap failed → cache fallback")
    urls = load_cache()

    if not urls:
        print("[FATAL] no cache")
        exit(1)

else:
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
# 2. 종료 조건
# -----------------------------
if not urls:
    print("[WARN] empty result")
    exit(0)

# -----------------------------
# 3. 그룹화
# -----------------------------
grouped = {}

for url in urls:
    time.sleep(0.3)

    category = "General"

    try:
        r = requests.get(url, headers=headers, timeout=30)
        page = BeautifulSoup(r.text, "html.parser")

        meta = page.find("meta", property="og:title")
        title = meta["content"] if meta and meta.get("content") else ""

        category = classify(url, title)

    except:
        category = "General"

    grouped.setdefault(category, []).append(url)

# -----------------------------
# 4. MD 생성 (🔥 전부 고정 유지)
# -----------------------------
with open(output_file, "w", encoding="utf-8") as f:

    # 🔥 FRONT MATTER 완전 고정
    f.write("---\n")
    f.write("layout: page\n")
    f.write(f"title: 요즘IT Weekly - {today_str}\n")
    f.write(f"permalink: /weekly/yozmit/{today_str}/\n")
    f.write("---\n\n")

    # 🔥 본문 헤더도 고정
    f.write(f"# 요즘IT Weekly - {today_str}\n\n")
    f.write("## Articles\n\n")

    # 🔥 내용만 변경됨 (링크 + 카테고리)
    for category, links in grouped.items():
        f.write(f"## {category}\n")
        for link in links:
            f.write(f"- {link}\n")
        f.write("\n")

print(f"[DONE] created: {output_file}")
