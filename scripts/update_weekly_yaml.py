import yaml
from pathlib import Path

weekly = {
    "geeknews": [],
    "yozmit": []
}

weekly_dir = Path("_weekly")

if weekly_dir.exists():

    for md in sorted(
        weekly_dir.glob("geeknews-*.md"),
        reverse=True
    ):

        name = md.stem.replace(
            "geeknews-",
            ""
        )

        weekly["geeknews"].append(
            {
                "title": f"GeekNews Weekly - {name}",
                "url": f"/weekly/geeknews/{name}/"
            }
        )

    for md in sorted(
        weekly_dir.glob("yozmit-*.md"),
        reverse=True
    ):

        name = md.stem.replace(
            "yozmit-",
            ""
        )

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
