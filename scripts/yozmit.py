import requests, re
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta
from dateutil import parser

SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap-news.xml"

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")

output_dir = Path("_weekly")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"yozmit-{today_str}.md"

if output_file.exists():
    print(f"[SKIP] already exists: {output_file}")
    exit(0)

headers = {
    "User-Agent": "Mozilla/5.0"
}

print("[INFO] Fetching sitemap...")
response = requests.get(SITEMAP_URL, timeout=30, headers=headers)

print("[INFO] status:", response.status_code)
print("[INFO] content length:", len(response.text))

# 안정적인 XML 파서
soup = BeautifulSoup(response.content, "lxml-xml")

urls = []

week_ago = today.date() - timedelta(days=7)

items = soup.find_all("url")
print("[INFO] total urls in sitemap:", len(items))

def clean_title(title: str) -> str:
    # 요즘IT 같은 "| 요즘IT" 제거
    title = re.sub(r"\s*\|\s*요즘IT.*", "", title)

    # 혹시 다른 사이트용 여유 처리
    title = re.sub(r"\s*\|.*$", "", title)

    return title.strip()

for item in items:
    loc = item.find("loc")
    lastmod = item.find("lastmod")

    if not loc or not lastmod:
        continue

    try:
        modified = parser.parse(lastmod.text.strip()).date()

        if modified >= week_ago:
            urls.append(loc.text.strip())

    except Exception as e:
        print("[PARSE ERROR]", lastmod.text, repr(e))

print(f"[INFO] Weekly Articles: {len(urls)}")

# MD 생성
with open(output_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: page\n")
    f.write(f"title: 요즘IT Weekly - {today_str}\n")
    f.write(f"permalink: /weekly/yozmit/{today_str}/\n")
    f.write("---\n\n")

    f.write(f"# 요즘IT Weekly - {today_str}\n\n")
    f.write("## Articles\n\n")

    if not urls:
        f.write("> No articles found this week.\n")
        print("[WARN] No URLs collected")

    for url in urls:
        try:
            html = requests.get(url, timeout=30, headers=headers)
            page = BeautifulSoup(html.text, "html.parser")

            meta = page.find("meta", property="og:title")

            if meta and meta.get("content"):
                title = clean_title(meta["content"].strip())
            elif page.title:
                title = page.title.get_text(strip=True)
            else:
                title = "Untitled"

            f.write(f"- [{title}]({url})\n")
            print("[OK]", title)

        except Exception as e:
            print("[ERROR URL]", url, repr(e))

print(f"[DONE] created: {output_file}")
