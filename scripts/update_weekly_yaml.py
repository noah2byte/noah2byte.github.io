import yaml
from pathlib import Path

weekly = {
    "geeknews": [],
    "yozmit": []
}

for md in sorted(
    Path("weekly/geeknews").glob("*.md"),
    reverse=True
):
    name = md.stem

    weekly["geeknews"].append({
        "title": f"GeekNews Weekly - {name}",
        "url": f"/weekly/geeknews/{name}/"
    })

for md in sorted(
    Path("weekly/yozmit").glob("*.md"),
    reverse=True
):
    name = md.stem

    weekly["yozmit"].append({
        "title": f"요즘IT Weekly - {name}",
        "url": f"/weekly/yozmit/{name}/"
    })

Path("_data").mkdir(exist_ok=True)

with open(
    "_data/weekly.yml",
    "w",
    encoding="utf-8"
) as f:
    yaml.dump(
        weekly,
        f,
        allow_unicode=True,
        sort_keys=False
    )

print("weekly.yml updated")
