#!/usr/bin/env python3
"""Collect release, artifact, and paper candidates for editorial review."""

import argparse
from datetime import UTC, datetime, timedelta
from html import escape
import json
import os
from pathlib import Path
import re
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zoneinfo import ZoneInfo


KST = ZoneInfo("Asia/Seoul")
RECENT_DAYS = 7
RETENTION_DAYS = 45
MAX_BYTES = 8 * 1024 * 1024
GITHUB = "https://api.github.com"
HUB = "https://huggingface.co"
WATCHED = (
    "isaac-sim/IsaacSim", "isaac-sim/IsaacLab", "newton-physics/newton", "NVIDIA/warp",
    "NVIDIA/Isaac-GR00T", "NVIDIA/cosmos", "NVIDIA/cosmos-framework", "NVlabs/alpasim",
    "NVlabs/alpamayo2", "NVlabs/alpamayo2-edge", "NVlabs/RoboLab",
    "black-forest-labs/flux-action", "runwayml/praxis-1-oss", "mimic-video/mimic-video",
)
ORGS = ("NVIDIA", "NVlabs", "isaac-sim", "NVIDIA-Omniverse", "NVIDIA-NeMo", "nvidia-cosmos")
RELATED = re.compile(
    r"robot|isaac|gr00t|cosmos|alpamayo|alpasim|nurec|physical.?ai|omniverse|"
    r"world[- ](?:action|model|simulat)|video[- ]action|manipulat|dexter|"
    r"autonomous[- ]driv|sim[- ]to[- ]real|splatting|digital[- ]twin",
    re.I,
)
PAPER_QUERY = "cat:cs.RO AND (abs:\"world action model\" OR abs:\"video action model\" OR abs:\"vision language action\" OR abs:\"Isaac Lab\" OR abs:\"Cosmos\" OR abs:\"GR00T\")"


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)


def fetch(url, json_response=True):
    headers = {"User-Agent": "awesome-nvidia-physical-ai-research/1.0"}
    if url.startswith(GITHUB + "/"):
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
    for attempt in range(2):
        try:
            with urlopen(Request(url, headers=headers), timeout=15) as response:
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError("response exceeds size limit")
                return json.loads(data) if json_response else ElementTree.fromstring(data)
        except HTTPError as error:
            if attempt or error.code not in {429, 500, 502, 503, 504}:
                raise
            delay = error.headers.get("Retry-After", "4")
            if not delay.isdigit() or int(delay) > 30:
                raise
            sleep(max(4, int(delay)))
        except (TimeoutError, URLError):
            if attempt:
                raise
            sleep(4)


def entry(key, title, url, date, detail, revision=""):
    target = urlsplit(url)
    if target.scheme != "https" or target.hostname not in {
        "github.com", "huggingface.co", "developer.nvidia.com", "research.nvidia.com", "arxiv.org",
    }:
        raise ValueError("unexpected source URL")
    url = quote(url, safe=":/?&=%#@+.,;_-~")
    return {
        "id": str(key), "title": title, "url": url, "date": instant(date).isoformat(),
        "detail": detail, "revision": revision,
    }


def github_releases(repo, cutoff):
    for item in fetch(f"{GITHUB}/repos/{repo}/releases?per_page=30"):
        published = item.get("published_at")
        updated = item.get("updated_at") or published
        if item["draft"] or not published or max(instant(published), instant(updated)) < cutoff:
            continue
        label = "프리릴리스" if item["prerelease"] else "릴리스"
        yield entry(item["id"], f"{repo} · {item['tag_name']}", item["html_url"],
                    max(instant(published), instant(updated)).isoformat(), label, item["tag_name"])


def github_repos(org, cutoff):
    for item in fetch(f"{GITHUB}/orgs/{org}/repos?type=public&sort=created&direction=desc&per_page=50"):
        if item["fork"] or instant(item["created_at"]) < cutoff:
            continue
        if RELATED.search(f"{item['name']} {item.get('description') or ''}"):
            license_id = (item.get("license") or {}).get("spdx_id") or "미확인"
            yield entry(item["id"], item["full_name"], item["html_url"], item["created_at"],
                        f"신규 저장소 · GitHub 라이선스 표기 {license_id}")


def github_license(repo, _cutoff):
    url = f"{GITHUB}/repos/{repo}/license"
    try:
        item = fetch(url)
    except HTTPError as error:
        if error.code == 404:
            yield entry(repo, f"{repo} · LICENSE", f"https://github.com/{repo}",
                        "1970-01-01", "라이선스 API에서 원문을 확인하지 못함")
            return
        raise
    license_id = (item.get("license") or {}).get("spdx_id") or "미확인"
    yield entry(repo, f"{repo} · {item['path']}", item["html_url"], "1970-01-01",
                f"GitHub 라이선스 표기 {license_id}", item["sha"])


def hub_items(kind, author, search, cutoff):
    params = [("author", author), ("search", search), ("limit", 50), ("sort", "lastModified")]
    params += [("expand[]", field) for field in ("sha", "gated", "cardData", "lastModified")]
    for item in fetch(f"{HUB}/api/{kind}?{urlencode(params)}"):
        updated = item["lastModified"]
        if instant(updated) < cutoff:
            continue
        terms = (item.get("cardData") or {}).get("license") or "미확인"
        gated = item.get("gated")
        if gated in {"auto", "manual", True}:
            access = "접근 절차 필요"
        elif gated is False:
            access = "접근 제한 표시 없음"
        else:
            access = "접근 상태 미확인"
        prefix = "datasets/" if kind == "datasets" else ""
        yield entry(item["id"], item["id"], f"{HUB}/{prefix}{item['id']}", updated,
                    f"{access} · 모델/데이터 카드 라이선스 {terms}", item.get("sha") or "")


def xml_text(node, name):
    return node.findtext(f"{{*}}{name}", "").strip()


def nvidia_blog(cutoff):
    url = "https://developer.nvidia.com/blog/category/robotics/feed/"
    for node in fetch(url, False).findall("{*}entry"):
        link = node.find("{*}link[@rel='alternate']")
        updated = xml_text(node, "updated") or xml_text(node, "published")
        if link is not None and updated and instant(updated) >= cutoff:
            yield entry(xml_text(node, "id") or link.attrib["href"], xml_text(node, "title"),
                        link.attrib["href"], updated, "NVIDIA Robotics 기술 블로그")


def nvidia_research(cutoff):
    root = fetch("https://research.nvidia.com/sitemap.xml", False)
    for node in root.findall("{*}url"):
        link = xml_text(node, "loc")
        updated = xml_text(node, "lastmod")
        slug = urlsplit(link).path
        if slug.startswith("/publication/") and RELATED.search(slug) and updated and instant(updated) >= cutoff:
            title = re.sub(r"^\d{4}-\d{2}_", "", slug.rsplit("/", 1)[-1]).replace("-", " ")
            yield entry(link, title, link, updated, "NVIDIA Research · 사이트맵 수정일")


def arxiv_papers(cutoff):
    params = {"search_query": PAPER_QUERY, "max_results": 100, "sortBy": "lastUpdatedDate",
              "sortOrder": "descending"}
    url = f"https://export.arxiv.org/api/query?{urlencode(params)}"
    for node in fetch(url, False).findall("{*}entry"):
        updated = xml_text(node, "updated")
        match = re.fullmatch(r"https?://arxiv.org/abs/(\d{4}\.\d{4,5})(v\d+)?", xml_text(node, "id"))
        if match and updated and instant(updated) >= cutoff:
            paper, version = match.groups()
            yield entry(paper, xml_text(node, "title"), f"https://arxiv.org/abs/{paper}",
                        updated, "arXiv 프리프린트 · 논문 수정일", version or "")


def sources():
    for repo in WATCHED:
        yield f"GitHub 릴리스 · {repo}", github_releases, (repo,)
        yield f"GitHub 라이선스 · {repo}", github_license, (repo,)
    for org in ORGS:
        yield f"GitHub 신규 저장소 · {org}", github_repos, (org,)
    for kind in ("models", "datasets"):
        for family in ("Cosmos", "GR00T", "Alpamayo", "PhysicalAI"):
            yield f"Hugging Face {kind} · nvidia/{family}", hub_items, (kind, "nvidia", family)
    for owner, family in (("black-forest-labs", "action"), ("runwayml", "praxis"), ("GEAR-Dreams", "dreamzero")):
        yield f"Hugging Face models · {owner}/{family}", hub_items, ("models", owner, family)
    yield "NVIDIA Robotics Atom", nvidia_blog, ()
    yield "NVIDIA Research 사이트맵", nvidia_research, ()
    yield "arXiv cs.RO", arxiv_papers, ()


def collect(previous, now, inputs):
    states, changes = {}, []
    baseline = now - timedelta(days=RECENT_DAYS)
    expiry = now - timedelta(days=RETENTION_DAYS)
    for name, query, args in inputs:
        saved = previous.get("sources", {}).get(name, {})
        last_success = saved.get("last_success")
        cutoff = min(baseline, instant(last_success) - timedelta(days=1)) if last_success else baseline
        known = {key: value for key, value in saved.get("items", {}).items()
                 if instant(value["date"]) >= expiry or value["date"].startswith("1970-")}
        try:
            records = list(query(*args, cutoff))
        except (OSError, ValueError, KeyError, TypeError, ElementTree.ParseError) as error:
            reason = f"HTTP {error.code}" if isinstance(error, HTTPError) else type(error).__name__
            states[name] = {
                "last_success": last_success, "error": reason,
                "first_failure": saved.get("first_failure") or now.isoformat(), "items": known,
            }
            print(f"Failed: {name} ({reason})")
            continue
        for record in records:
            key = record["id"]
            old = known.get(key)
            if old != record and (old or instant(record["date"]) >= cutoff):
                changes.append({**record, "source": name, "detected": now.isoformat()})
            known[key] = record
        states[name] = {"last_success": now.isoformat(), "error": None, "items": known}
        print(f"Checked: {name} ({len(records)})")
    recent = {
        item["url"]: item
        for item in previous.get("recent", []) + changes
        if instant(item["detected"]) >= baseline
    }
    return {
        "checked": now.isoformat(), "sources": states, "recent": list(recent.values()),
        "changes": len({item["url"] for item in changes}),
    }


def md_text(text):
    text = escape(" ".join(str(text).split()), quote=False)
    return re.sub(r"([\\`*_{}\[\]()|])", r"\\\1", text)


def local_time(date):
    return instant(date).astimezone(KST).strftime("%Y-%m-%d %H:%M KST") if date else "기록 없음"


def report(state):
    errors = [(name, source) for name, source in state["sources"].items() if source["error"]]
    lines = [
        "# NVIDIA Physical AI 연구 수집 결과", "",
        f"확인 시각 {local_time(state['checked'])} · 새로 발견하거나 변경된 항목 {state['changes']}건", "",
        "아래 항목은 검토 후보입니다. 날짜는 출처의 발표 또는 수정 시각입니다. "
        "코드·모델·데이터셋의 실제 공개 여부와 이용 조건은 각 원문에서 확인합니다.", "",
        "## 최근 7일에 발견한 후보", "",
    ]
    if not state["recent"]:
        lines += ["최근 7일에 발견한 변경이 없습니다.", ""]
    else:
        latest = sorted(state["recent"], key=lambda item: (item["detected"], item["date"]), reverse=True)
        for item in latest:
            date = "날짜 미제공" if item["date"].startswith("1970-") else item["date"][:10]
            lines.append(f"- [{md_text(item['title'])}]({item['url']}) · {date} · {md_text(item['detail'])}")
        lines.append("")
    lines += ["## 출처별 상태", "", f"확인 성공 {len(state['sources']) - len(errors)}개 · 실패 {len(errors)}개", ""]
    for name, source in state["sources"].items():
        status = source["error"] or "성공"
        lines.append(f"- {md_text(name)} · {status} · 마지막 성공 {local_time(source['last_success'])}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text()) if args.previous.is_file() else {}
    state = collect(previous, datetime.now(UTC), sources())
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    (args.output / "latest.md").write_text(report(state))
    if instant(state["checked"]).astimezone(KST).weekday() == 4:
        (args.output / "weekly.md").write_text(report(state))
    print(f"{state['changes']} changed entries")


if __name__ == "__main__":
    main()
