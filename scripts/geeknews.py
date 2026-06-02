import feedparser
from pathlib import Path
from datetime import datetime

RSS_URL = "https://news.hada.io/rss/news"

today = datetime.now().strftime("%Y-%m-%d")

output_dir = Path("_weekly/geeknews")
output_dir.mkdir(parents=True, exist_ok=True)

output_file = output_dir / f"{today}.md"

if output_file.exists():
    print(f"{output_file} already exists")
    exit(0)

feed = feedparser.parse(RSS_URL)

with open(output_file, "w", encoding="utf-8") as f:
    f.write("---\n")
    f.write("layout: page\n")
    f.write(f"title: GeekNews Weekly - {today}\n")
    f.write(f"permalink: /weekly/geeknews/{today}/\n")
    f.write("---\n\n")

    f.write(f"# GeekNews Weekly - {today}\n\n")
    f.write("## Articles\n\n")

    for entry in feed.entries[:30]:
        title = entry.title.strip()
        link = entry.link.strip()

        f.write(f"- [{title}]({link})\n")

print(f"Created {output_file}")
