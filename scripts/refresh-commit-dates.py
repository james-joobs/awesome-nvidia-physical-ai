"""Refresh the open-source catalog's default-branch commit dates from GitHub."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
CATALOGS = {
    "README.md": ("## 1. Projects with confirmed open-source code", "Archived"),
    "README.ko.md": ("## 1. 오픈소스 코드가 확인된 프로젝트", "보관됨"),
}
GITHUB_REPO = re.compile(r"https://github\.com/([\w.-]+/[\w.-]+)(?=[/)|#?\s]|$)")
FIELDS = """
  isArchived
  nameWithOwner
  defaultBranchRef {
    target {
      ... on Commit { oid committedDate }
    }
  }
"""


def catalog_rows(text, heading):
    lines = text.splitlines(keepends=True)
    first = lines.index(heading + "\n") + 1
    for index in range(first, len(lines)):
        line = lines[index]
        if line.startswith("## "):
            break
        if not line.startswith("| **"):
            continue
        cells = line.strip().removeprefix("| ").removesuffix(" |").split(" | ")
        if len(cells) != 6:
            raise ValueError(f"Expected six cells in {line.rstrip()}")
        repo = GITHUB_REPO.search(cells[4])
        if repo is None:
            raise ValueError(f"Missing GitHub source in {line.rstrip()}")
        yield index, cells, repo[1].lower()


def fetch_commits(repositories, token):
    commits = {}
    names = sorted(repositories)
    for start in range(0, len(names), 20):
        batch = names[start:start + 20]
        parts = []
        for index, repo in enumerate(batch):
            owner, name = map(json.dumps, repo.split("/"))
            parts.append(f"r{index}: repository(owner: {owner}, name: {name}) {{ {FIELDS} }}")
        query = "query { " + " ".join(parts) + " }"
        request = Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query}).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "awesome-nvidia-physical-ai-catalog",
            },
        )
        with urlopen(request, timeout=30) as response:
            payload = json.load(response)
        if payload.get("errors"):
            raise RuntimeError(f"GitHub GraphQL errors: {payload['errors']}")
        for index, repo in enumerate(batch):
            data = payload["data"][f"r{index}"]
            branch = data and data["defaultBranchRef"]
            commit = branch and branch["target"]
            if not commit or not commit.get("oid"):
                raise RuntimeError(f"Could not resolve the default-branch commit for {repo}")
            date = datetime.fromisoformat(commit["committedDate"]).astimezone(timezone.utc).date()
            url = f"https://github.com/{data['nameWithOwner']}/commit/{commit['oid']}"
            commits[repo] = (date, url, data["isArchived"])
    return commits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing files.")
    args = parser.parse_args()
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        parser.exit(2, "Set GH_TOKEN or GITHUB_TOKEN to query GitHub.\n")

    catalogs = []
    for name, (heading, archived) in CATALOGS.items():
        path = ROOT / name
        original = path.read_text(encoding="utf-8")
        rows = list(catalog_rows(original, heading))
        if not rows:
            raise RuntimeError(f"No open-source project rows in {name}")
        catalogs.append((path, original, rows, archived))

    english = [repo for _, _, repo in catalogs[0][2]]
    korean = [repo for _, _, repo in catalogs[1][2]]
    if english != korean:
        raise RuntimeError("English and Korean open-source tables list different repositories")

    commits = fetch_commits(set(english), token)
    changed = []
    for path, original, rows, archived in catalogs:
        lines = original.splitlines(keepends=True)
        for index, cells, repo in rows:
            date, url, is_archived = commits[repo]
            cells[3] = f"[{date}]({url})" + (f" · {archived}" if is_archived else "")
            lines[index] = "| " + " | ".join(cells) + " |\n"
        updated = "".join(lines)
        if updated != original:
            changed.append(path.name)
            if not args.check:
                path.write_text(updated, encoding="utf-8")

    print(f"Checked {len(english)} entries across {len(commits)} GitHub repositories.")
    if changed:
        print(("Needs refresh: " if args.check else "Updated: ") + ", ".join(changed))
    else:
        print("Both README files are current.")
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
