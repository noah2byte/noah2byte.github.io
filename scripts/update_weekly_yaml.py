import yaml
from pathlib import Path

weekly = {
    "geeknews": [],
    "yozmit": []
}

geeknews_dir = Path("weekly/geeknews")
yozmit_dir = Path("weekly/yozmit")

if geeknews_dir.exists():

    for md in sorted(
        geeknews_dir.glob("*.md"),
        reverse=True
    ):

        name = md.stem

        weekly["geeknews"].append(
            {
                "title": f"GeekNews Weekly - {name}",
                "url": f"/weekly/geeknews/{name}/"
            }
        )

if yozmit_dir.exists():

    for md in sorted(
        yozmit_dir.glob("*.md"),
        reverse=True
    ):

        name = md.stem

        weekly["yozmit"].append(
            {
                "title": f"요즘IT Weekly - {name}",
                "url": f"/weekly/yozmit/{name}/"
            }
        )

Path("_data").mkdir(
    exist_ok=True
)

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

print(
    "_data/weekly.yml updated"
)
