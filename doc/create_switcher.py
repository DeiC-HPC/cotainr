import subprocess
import json

tags = [
    tag
    for tag in (
        subprocess.run(
            ["git", "--no-pager", "tag"], capture_output=True, text=True
        ).stdout.splitlines()
    )
    if tag.startswith("20")
]
tags.reverse()

switcher = [
    {
        "name": "dev",
        "version": "latest",
        "url": "https://cotainr.readthedocs.io/en/latest/",
    },
    {
        "name": f"{tags[0]} (stable)",
        "version": "stable",
        "url": "https://cotainr.readthedocs.io/en/stable/",
    },
]

for tag in tags[1:4]:
    switcher.append(
        {
            "name": tag,
            "version": tag,
            "url": f"https://cotainr.readthedocs.io/en/{tag}/",
        }
    )


with open("_static/switcher.json", "w") as f:
    json.dump(switcher, f)
