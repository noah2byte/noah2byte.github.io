import requests
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime

SITEMAP_URL = "https://yozm.wishket.com/magazine/sitemap.xml"

today = datetime.now().strftime("%Y-%m-%d")

output_dir = Path("weekly/yozmit")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"{today}.md"

if output_file.exists():
    print(f"{output_file} already exists")
    exit(0)

xml = requests.get(SITEMAP_URL, timeout=30).text

soup = BeautifulSoup(xml, "xml")

urls = []

for loc in soup.find_all("loc"):
    url = loc.text.strip()

    if "/magazine/detail/" in url:
        urls.append(url)

urls = urls[-30:]

with open(output_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: page\n")
    f.write(f"title: 요즘IT Weekly - {today}\n")
    f.write(f"permalink: /weekly/yozmit/{today}/\n")
    f.write("---\n\n")

    f.write(f"# 요즘IT Weekly - {today}\n\n")
    f.write("## Articles\n\n")

    for url in urls:
        try:
            html = requests.get(url, timeout=30).text

            page = BeautifulSoup(html, "html.parser")

            title = page.title.text.strip()

            f.write(f"- [{title}]({url})\n")

        except Exception as e:
            print(e)

print(f"Created {output_file}")
