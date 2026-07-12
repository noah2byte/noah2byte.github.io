import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import requests
from bs4 import BeautifulSoup
from dateutil import parser
import urllib.robotparser as robotparser

# -----------------------------
# 설정
# -----------------------------
SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap-news.xml"
BASE_URL = "https://yozm.wishket.com"
DAYS_BACK = 7               # 최근 며칠치를 모을지
DEFAULT_REQUEST_DELAY = 5   # robots.txt에 Crawl-delay가 없을 때 쓸 기본값(초)
TIMEOUT = 30

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")

output_dir = Path("_weekly")
cache_dir = Path("_cache")
output_dir.mkdir(parents=True, exist_ok=True)
cache_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"yozmit-{today_str}.md"
cache_file = cache_dir / "links-cache.json"

headers = {
    # 큐레이션 봇임을 정직하게 밝힘 (예의 + 문제 발생 시 식별 가능)
    "User-Agent": "noah2byte-weekly-digest/1.0 (personal tech blog curation)"
}

# 카테고리 분류 규칙 (순서 = 우선순위)
CATEGORY_RULES = [
    ("AI / LLM",         ["ai", "gpt", "llm", "prompt", "rag", "agent"]),
    ("DevOps / Infra",   ["kubernetes", "docker", "devops", "ci/cd", "terraform"]),
    ("Backend / System", ["api", "server", "backend", "database", "architecture"]),
    ("Security",         ["security", "oauth", "auth", "attack"]),
    ("Frontend / UX",    ["ui", "ux", "frontend", "design"]),
]


# -----------------------------
# robots.txt
# -----------------------------
rp = robotparser.RobotFileParser()
rp.set_url(f"{BASE_URL}/robots.txt")
try:
    rp.read()
except Exception as e:
    print(f"[WARN] robots.txt load failed: {e}")

# robots.txt에 명시된 Crawl-delay를 실제로 지킨다. 없으면 기본값 사용.
REQUEST_DELAY = rp.crawl_delay(headers["User-Agent"]) or DEFAULT_REQUEST_DELAY
REQUEST_DELAY = float(REQUEST_DELAY)
print(f"[INFO] request delay: {REQUEST_DELAY}s")


def allowed(url: str) -> bool:
    try:
        return rp.can_fetch(headers["User-Agent"], url)
    except Exception:
        return True


# -----------------------------
# cache (sitemap 실패 시 폴백용)
# -----------------------------
def load_cache():
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8"))
    return []


def save_cache(data):
    cache_file.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# -----------------------------
# sitemap 수집
# -----------------------------
def fetch_sitemap():
    try:
        r = requests.get(SITEMAP_URL, headers=headers, timeout=TIMEOUT)
        if r.status_code == 200:
            return r
        print(f"[WARN] sitemap status: {r.status_code}")
    except Exception as e:
        print(f"[WARN] sitemap request failed: {e}")
    return None


def collect_urls():
    """sitemap에서 최근 DAYS_BACK일 이내 URL 목록을 수집. 실패 시 캐시 폴백."""
    response = fetch_sitemap()
    if not response:
        print("[WARN] sitemap failed → cache fallback")
        cached = load_cache()
        if not cached:
            print("[FATAL] no cache available")
            raise SystemExit(1)
        return cached

    soup = BeautifulSoup(response.content, "lxml-xml")
    items = soup.find_all("url")
    week_ago = today.date() - timedelta(days=DAYS_BACK)

    urls = []
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
        except Exception:
            continue

        if modified >= week_ago:
            urls.append(url)

    if urls:
        save_cache(urls)
    return urls


# -----------------------------
# 제목 가져오기 + 카테고리 분류
# -----------------------------
def classify(url: str, title: str) -> str:
    text = (url + " " + title).lower()
    for category, keywords in CATEGORY_RULES:
        if any(k in text for k in keywords):
            return category
    return "General"


def fetch_title(url: str) -> str:
    """og:title만 추출. 본문은 저장하지 않는다 (링크 큐레이션 원칙)."""
    try:
        r = requests.get(url, headers=headers, timeout=TIMEOUT)
        page = BeautifulSoup(r.text, "html.parser")
        meta = page.find("meta", property="og:title")
        if meta and meta.get("content"):
            return meta["content"].strip()
    except Exception:
        pass
    return ""


# -----------------------------
# 마크다운 생성
# -----------------------------
def write_markdown(grouped: dict):
    with open(output_file, "w", encoding="utf-8") as f:
        # front matter (고정)
        f.write("---\n")
        f.write("layout: page\n")
        f.write(f"title: 요즘IT Weekly - {today_str}\n")
        f.write(f"permalink: /weekly/yozmit/{today_str}/\n")
        f.write("---\n\n")

        f.write(f"# 요즘IT Weekly - {today_str}\n\n")

        # 출처 명시 (저작권 존중 + 큐레이션 성격 명확화)
        f.write(
            "> 본 페이지는 [요즘IT](https://yozm.wishket.com) 매거진의 "
            "공개 아티클을 제목·링크 형태로 큐레이션한 것입니다. "
            "각 글의 저작권은 원저작자 및 요즘IT에 있으며, "
            "제목을 클릭하면 원문으로 이동합니다.\n\n"
        )

        total = sum(len(v) for v in grouped.values())
        f.write(f"이번 주 수집된 아티클: 총 {total}건\n\n")

        # 카테고리 순서를 규칙 순서대로 고정 (General은 맨 뒤)
        ordered = [name for name, _ in CATEGORY_RULES] + ["General"]
        for category in ordered:
            items = grouped.get(category)
            if not items:
                continue
            f.write(f"## {category}\n\n")
            for title, link in items:
                if title:
                    f.write(f"- [{title}]({link})\n")
                else:
                    f.write(f"- <{link}>\n")
            f.write("\n")


# -----------------------------
# main
# -----------------------------
def main():
    urls = collect_urls()
    print(f"[INFO] collected urls: {len(urls)}")

    if not urls:
        print("[WARN] empty result - nothing to write")
        return

    grouped = {}
    for url in urls:
        time.sleep(REQUEST_DELAY)
        title = fetch_title(url)
        category = classify(url, title)
        grouped.setdefault(category, []).append((title, url))

    write_markdown(grouped)
    print(f"[DONE] created: {output_file}")


if __name__ == "__main__":
    main()