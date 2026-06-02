import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timedelta

SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap-news.xml"

today = datetime.now()
today_str = today.strftime("%Y-%m-%d")

output_dir = Path("_weekly")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"yozmit-{today_str}.md"

if output_file.exists():
    print(f"{output_file} already exists")
    exit(0)

response = requests.get(
    SITEMAP_URL,
    timeout=30,
    headers={
        "User-Agent": "Mozilla/5.0"
    }
)

soup = BeautifulSoup(response.text, "xml")

week_ago = today.date() - timedelta(days=7)

urls = []

for item in soup.find_all("url"):

    loc = item.find("loc")
    lastmod = item.find("lastmod")

    if not loc or not lastmod:
        continue

    try:
        modified = datetime.strptime(
            lastmod.text.strip(),
            "%Y-%m-%d"
        ).date()

        if modified >= week_ago:
            urls.append(loc.text.strip())

    except Exception as e:
        print(e)

print(f"Weekly Articles: {len(urls)}")

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

            html = requests.get(
                url,
                timeout=30,
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            page = BeautifulSoup(
                html.text,
                "html.parser"
            )

            title_tag = page.find(
                "meta",
                property="og:title"
            )

            if title_tag:
                title = title_tag.get(
                    "content",
                    ""
                ).strip()
            else:
                title = page.title.get_text(
                    strip=True
                )

            print(title)

            f.write(
                f"- [{title}]({url})\n"
            )

        except Exception as e:
            print(
                f"ERROR: {url}"
            )
            print(e)

print(f"Created {output_file}")
