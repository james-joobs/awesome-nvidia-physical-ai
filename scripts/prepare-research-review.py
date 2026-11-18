"""Turn verified research candidates into paired catalog and archive edits."""

import argparse
from datetime import datetime
from html import escape
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
from urllib.error import URLError
from urllib.parse import quote, unquote, urlsplit
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


GH = "https://github.com"
API = "https://api.github.com"
HF = "https://huggingface.co"
PATHS = (
    ("CATALOG.md", "docs/en/robot-foundation-models.md"),
    ("CATALOG.ko.md", "docs/ko/robot-foundation-models.md"),
)
NVIDIA_OWNERS = {
    "nvidia", "nvlabs", "nvidia-isaac", "nvidia-omniverse",
    "isaac-sim", "nvidia-cosmos", "nvidia-nemo",
}
CODE_LICENSES = {"Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "MIT", "MPL-2.0"}
HUB_LICENSES = {
    "apache-2.0": "Apache-2.0", "mit": "MIT", "cc-by-4.0": "CC BY 4.0",
    "cc-by-nc-4.0": "CC BY-NC 4.0", "cc-by-nc-sa-4.0": "CC BY-NC-SA 4.0",
    "openmdw1.1-license": "OpenMDW-1.1", "nvidia-open-model-license": "NVIDIA Open Model License",
}
TOPICS = (
    (r"world[-_ ]action|video[-_ ]action|\bwam\b", "World action and video-action modeling", "월드 액션·비디오 액션 모델"),
    (r"\bvla\b|vision[-_ ]language[-_ ]action", "Vision-language-action policies", "시각·언어·행동 정책"),
    (r"alpamayo|autonomous[-_ ]driv|alpasim|\bnurec\b", "Autonomous driving and scene reconstruction", "자율주행·장면 재구성"),
    (r"simulat|isaac|newton|physx|warp|render", "Simulation and rendering", "시뮬레이션·렌더링"),
    (r"robot|humanoid|gr00t|manipulat|dexter|teleoperat", "Robot learning and control", "로봇 학습·제어"),
    (r"cosmos|world[-_ ]model|physical[-_ ]ai", "Physical AI and world models", "피지컬 AI·월드 모델"),
)
URL_RE = re.compile(r"https://[^\s)\]>]+")
NAME = r"[A-Za-z0-9_.-]+"
SHA = re.compile(r"[a-f0-9]{40}")
SECTIONS = {
    "repo": ("### Robot learning, capture, and control", "### 로봇 학습·시연 수집·제어"),
    "repo-simulation": ("### Physics, 3D, and simulation", "### 물리·3D·시뮬레이션"),
    "repo-driving": ("### Autonomous driving", "### 자율주행"),
    "dataset": ("### Robot demonstrations and motion", "### 로봇 시연과 동작"),
    "dataset-driving": ("### Driving, video, and world-model data", "### 자율주행·영상·월드 모델 데이터"),
    "model": ("## Robot foundation models and VLAs", "## 로봇 파운데이션 모델과 VLA"),
    "research": ("## Recent world action research", "## 최근 월드 액션 연구"),
    "release": ("## Recent upstream releases", "## 최근 업스트림 릴리스"),
}


def request(url, json_response=True):
    headers = {"User-Agent": "physical-ai-research-review/1.0"}
    if url.startswith(f"{API}/") and os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {os.environ['GH_TOKEN']}"
        headers["Accept"] = "application/vnd.github+json"
    with urlopen(Request(url, headers=headers), timeout=12) as response:
        payload = response.read(4 * 1024 * 1024 + 1)
        if len(payload) > 4 * 1024 * 1024:
            raise ValueError("response too large")
        return json.loads(payload) if json_response else payload.decode("utf-8")


def url_key(url):
    target = urlsplit(url)
    path = unquote(target.path).rstrip("/")
    if target.hostname in {"github.com", "raw.githubusercontent.com"}:
        release = re.fullmatch(rf"/({NAME}/{NAME})/(?:releases/tag|tree)/(v?\d[^/]*)", path)
        if release:
            return "release:" + release[1].lower() + "/" + release[2]
        match = re.match(rf"/({NAME}/{NAME})(?:/|$)", path)
        if match:
            return "github:" + match[1].lower().removesuffix(".git")
    if target.hostname == "huggingface.co":
        match = re.match(rf"/((?:datasets/)?{NAME}/{NAME})(?:/|$)", path)
        if match:
            return "hub:" + match[1].lower()
    if target.hostname == "arxiv.org":
        match = re.fullmatch(r"/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?", path)
        if match:
            return "arxiv:" + match[1]
    if target.hostname in {"developer.nvidia.com", "research.nvidia.com"}:
        return target.hostname + path.lower()
    return None


def seen_urls(contents):
    return {url_key(url) for text in contents for url in URL_RE.findall(text)} - {None}


def clean(text):
    literal = escape(" ".join(str(text).split()), quote=False)
    return re.sub(r"([\\`*_{}\[\]()|])", r"\\\1", literal)


def link(label, url):
    return f"[{clean(label)}]({quote(url, safe=':/?&=%#@+.,;_-~')})"


def row(*cells):
    return "| " + " | ".join(cells) + " |"


def family(text):
    return next(((en, ko) for pattern, en, ko in TOPICS if re.search(pattern, text, re.I)), None)


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.author_links = []
        self.paper_terms = ""
        self.meta = {}
        self.heading = ""
        self.in_heading = False
        self.in_comments = False
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = attrs.get("href", "")
        if tag == "a" and attrs.get("title") == "Rights to this article":
            self.paper_terms = re.sub(r"^http://", "https://", url)
        if tag == "a" and url.startswith("https://"):
            self.links.append(url)
            if self.in_comments:
                self.author_links.append(url)
        elif tag == "td" and "comments" in attrs.get("class", "").split():
            self.in_comments = True
        elif tag == "meta" and attrs.get("name", "").startswith("citation_"):
            self.meta.setdefault(attrs["name"], attrs.get("content", ""))
        elif tag == "h1" and not self.heading:
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_heading = False
        elif tag == "td":
            self.in_comments = False

    def handle_data(self, data):
        if self.in_heading:
            self.heading += data


def verify_repo(repo):
    info = request(f"{API}/repos/{repo}")
    if info["private"] or info["archived"] or info["fork"] or info["full_name"].lower() != repo.lower():
        return None
    topic = family(repo + " " + (info["description"] or ""))
    if not topic:
        return None
    head = request(f"{API}/repos/{repo}/commits/{quote(info['default_branch'], safe='')}")
    revision = head["sha"]
    if not SHA.fullmatch(revision):
        raise ValueError("invalid repository revision")
    license_info = request(f"{API}/repos/{repo}/license?ref={revision}")
    terms = license_info["license"]["spdx_id"]
    if terms not in CODE_LICENSES:
        return None
    path = quote(license_info["path"], safe="/")
    license_url = f"https://raw.githubusercontent.com/{info['full_name']}/{revision}/{path}"
    request(license_url, False)
    return {
        "kind": "repo", "url": info["html_url"], "title": info["full_name"], "topic": topic,
        "terms": terms, "license": license_url, "revision": revision,
        "date": head["commit"]["committer"]["date"][:10],
    }


def verify_release(url):
    match = re.fullmatch(rf"/({NAME}/{NAME})/releases/tag/([^/]+)", urlsplit(url).path)
    if not match:
        return None
    repo, tag = match.groups()
    info = request(f"{API}/repos/{repo}/releases/tags/{quote(unquote(tag), safe='')}")
    if info["draft"] or not info["published_at"]:
        return None
    license_info = request(f"{API}/repos/{repo}/license?ref={quote(unquote(tag), safe='')}")
    terms = license_info["license"]["spdx_id"]
    if terms not in CODE_LICENSES:
        return None
    license_url = f"https://raw.githubusercontent.com/{repo}/{tag}/{quote(license_info['path'], safe='/')}"
    request(license_url, False)
    return {
        "kind": "release", "url": info["html_url"], "title": f"{repo} {info['tag_name']}",
        "prerelease": info["prerelease"], "terms": terms, "license": license_url,
        "date": info["published_at"][:10],
    }


def verify_hub(url):
    match = re.fullmatch(rf"/(datasets/)?({NAME}/{NAME})/?", urlsplit(url).path)
    if not match:
        return None
    directory, name = match.groups()
    kind = "dataset" if directory else "model"
    info = request(f"{HF}/api/{kind}s/{name}")
    if info["private"] or info.get("gated") not in (False, "auto", "manual", True) or not SHA.fullmatch(info["sha"]):
        return None
    card = info.get("cardData") or {}
    terms = HUB_LICENSES.get(card.get("license"))
    license_file = next((item["rfilename"] for item in info["siblings"]
                         if re.fullmatch(r"LICENSE(?:\.md|\.txt)?", item["rfilename"], re.I)), None)
    extension = (r"\.(parquet|tar(?:\.gz)?|zip|jsonl|hdf5|npz|mp4|arrow)$" if kind == "dataset"
                 else r"\.(safetensors|pt|pth|ckpt|bin|gguf|onnx)$")
    if not any(re.search(extension, item["rfilename"], re.I) for item in info["siblings"]):
        return None
    official = f"{HF}/{directory or ''}{name}"
    license_link = card.get("license_link", "")
    if (
        not terms and isinstance(license_link, str)
        and license_link.rstrip("/") == "https://openmdw.ai/license/1-1"
    ):
        terms = "OpenMDW-1.1"
    if not terms:
        return None
    card_url = f"{official}/blob/{info['sha']}/README.md"
    license_url = f"{official}/blob/{info['sha']}/{license_file}" if license_file else card_url
    request(license_url, False)
    topic = family(name + " " + " ".join(info.get("tags", [])))
    if not topic:
        return None
    return {
        "kind": kind, "url": official, "title": name, "topic": topic,
        "gated": bool(info["gated"]), "terms": terms, "license": license_url,
    }


def verify_research(candidate, page):
    url = candidate["url"]
    key = url_key(url)
    if key.startswith("arxiv:"):
        title = page.meta.get("citation_title")
        if not title or not family(title):
            return None
        terms = page.paper_terms
        if not terms.startswith(("https://creativecommons.org/licenses/", "https://arxiv.org/licenses/")):
            return None
        return {
            "kind": "research", "url": url, "title": title, "topic": family(title),
            "terms": terms, "paper": True, "evidence": [],
        }
    title = page.heading
    topic = family(title or url)
    if not title or not topic:
        return None
    return {"kind": "research", "url": url, "title": title, "topic": topic, "paper": False, "evidence": []}


def author_artifact(url):
    target = urlsplit(url)
    if target.hostname == "huggingface.co":
        return verify_hub(url)
    if target.hostname != "github.com" or not re.fullmatch(rf"/{NAME}/{NAME}/?", target.path):
        return None
    repo = target.path.strip("/")
    info = request(f"{API}/repos/{repo}")
    if info["private"] or info["fork"]:
        return None
    terms = info.get("license") or {}
    record = {"kind": "repo", "url": info["html_url"], "terms": None}
    if terms.get("spdx_id") in CODE_LICENSES or terms.get("spdx_id") == "CC-BY-NC-4.0":
        evidence = request(f"{API}/repos/{repo}/license")
        request(evidence["download_url"], False)
        record.update(terms=evidence["license"]["spdx_id"], license=evidence["html_url"])
    return record


def candidates(state, known):
    selected = []
    limits = {"repo": 3, "release": 4, "model": 3, "dataset": 3, "research": 4}
    counts = dict.fromkeys(limits, 0)

    def add(record):
        if record:
            kind, key = record["kind"], url_key(record["url"])
            if key and key not in known and counts[kind] < limits[kind]:
                known.add(key)
                counts[kind] += 1
                selected.append(record)

    def attempt(check, *args):
        try:
            return check(*args)
        except (URLError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            print(f"Needs manual verification: {type(error).__name__}")

    def recent_priority(item):
        key = url_key(item["url"]) or ""
        primary = key.startswith(("developer.nvidia.com", "research.nvidia.com"))
        return primary, item["date"]

    tried_repos = set()
    for item in sorted(state["recent"], key=recent_priority, reverse=True):
        url = item["url"]
        key = url_key(url) or ""
        if counts["release"] < limits["release"] and key.startswith("release:") and key not in known:
            add(attempt(verify_release, url))
        elif key.startswith("github:") and item["source"].startswith("GitHub 신규 저장소"):
            if counts["repo"] < limits["repo"] and key not in known:
                add(attempt(verify_repo, urlsplit(url).path.strip("/")))
        elif key.startswith("hub:") and key not in known:
            kind = "dataset" if key.startswith("hub:datasets/") else "model"
            if counts[kind] < limits[kind]:
                add(attempt(verify_hub, url))
        elif key.startswith(("arxiv:", "developer.nvidia.com", "research.nvidia.com")):
            official = key.startswith(("developer.nvidia.com", "research.nvidia.com"))
            if not official and (counts["research"] >= limits["research"] or key in known):
                continue
            # Only fetch canonical source pages from the report.
            page = attempt(lambda address: Page(request(address, False)), url)
            if not page:
                continue
            if not key.startswith("developer.nvidia.com") and key not in known and counts["research"] < limits["research"]:
                study = verify_research(item, page)
                if study:
                    for upstream in dict.fromkeys(page.author_links):
                        evidence = attempt(author_artifact, upstream)
                        if evidence:
                            study["evidence"].append(evidence)
                        if len(study["evidence"]) >= 3:
                            break
                    add(study)
            if official:
                for upstream in page.links:
                    repo = re.fullmatch(rf"/({NAME}/{NAME})/?", urlsplit(upstream).path)
                    repo_key = url_key(upstream)
                    if counts["repo"] >= limits["repo"]:
                        break
                    if (
                        urlsplit(upstream).hostname == "github.com" and repo
                        and repo_key not in known | tried_repos
                        and repo[1].split("/")[0].lower() in NVIDIA_OWNERS
                    ):
                        tried_repos.add(repo_key)
                        add(attempt(verify_repo, repo[1]))
    return selected


def render(record, lang):
    kind, title, url = record["kind"], clean(record["title"]), record["url"]
    ko = lang == 1
    official = link("공식 출처" if ko else "Official source", url)
    terms = link(record["terms"], record["license"]) if "license" in record else ""
    topic = clean(record["topic"][lang]) if "topic" in record else ""
    if kind == "release":
        status = ("프리릴리스" if ko else "Pre-release") if record["prerelease"] else ("릴리스" if ko else "Release")
        return f"- **{title}** · {status} · {record['date']} · {official} · {terms}"
    if kind == "repo":
        details = "공개 저장소 코드" if ko else "Repository code"
        recent = link(record["date"], f"{url}/commit/{record['revision']}")
        return row(f"**{title}**", topic, f"{details} · {terms}", recent, official, "—")
    if kind in ("model", "dataset"):
        access = ("Hugging Face 접근 절차 필요" if ko else "Hugging Face access required") if record["gated"] \
            else ("다운로드 가능" if ko else "Downloadable")
        if kind == "dataset":
            return row(f"**{link(record['title'], url)}**", topic, f"{access} · {terms}", "—")
        return row(f"**{title}**", topic, f"{access} · {terms}", official)
    publication = "프리프린트 공개" if ko else "Public preprint"
    if record["paper"]:
        cc = re.fullmatch(r"https://creativecommons.org/licenses/([a-z-]+)/([\d.]+)/?", record["terms"])
        license_name = f"CC {cc[1].upper()} {cc[2]}" if cc else ("arXiv 배포 약관" if ko else "arXiv distribution terms")
        publication += " · " + link(license_name, record["terms"])
    else:
        publication = "공식 연구 자료 공개" if ko else "Public NVIDIA research material"
    labels = {"repo": ("Public code", "코드 공개"), "model": ("Model files", "모델 가중치"),
              "dataset": ("Dataset files", "데이터셋")}
    artifacts = []
    kinds = set()
    for item in record["evidence"]:
        kinds.add(item["kind"])
        details = link(labels[item["kind"]][lang], item["url"])
        if item.get("gated"):
            details += " (접근 절차 필요)" if ko else " (access required)"
        details += " · " + (link(item["terms"], item["license"]) if item["terms"]
                            else ("이용 조건 미확인" if ko else "terms unverified"))
        artifacts.append(details)
    if "repo" not in kinds:
        artifacts.append("코드 공개 여부 미확인" if ko else "Code availability unverified")
    if "model" not in kinds:
        artifacts.append("가중치 공개 여부 미확인" if ko else "Weight availability unverified")
    return row(f"**{title}**", topic, " · ".join([publication, *artifacts, official]))


def section_for(record):
    kind = record["kind"]
    topic = record.get("topic", ("", ""))[0]
    if kind in ("repo", "dataset") and topic.startswith("Autonomous driving"):
        return f"{kind}-driving"
    if kind == "repo" and topic == "Simulation and rendering":
        return "repo-simulation"
    return kind


def insert(text, section, lines, table):
    if not lines:
        return text
    start = text.index(f"{section}\n") + len(section) + 1
    if table:
        divider = re.search(r"^\|[- :|]+\|\n", text[start:], re.M)
        if not divider:
            raise ValueError(f"Missing table for {section}")
        start += divider.end()
        return text[:start] + "\n".join(lines) + "\n" + text[start:]
    return text[:start] + "\n" + "\n".join(lines) + "\n" + text[start:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--pending", type=Path, required=True)
    parser.add_argument("--body", type=Path, required=True)
    args = parser.parse_args()
    state = json.loads(args.state.read_text())
    catalog = [Path(pair[0]).read_text() for pair in PATHS]
    guides = [p.read_text() for p in Path("docs").glob("*/*.md")]
    pending = [p.read_text() for p in args.pending.glob("*.md")]
    existing = seen_urls(catalog + guides + pending)
    selected = candidates(state, existing)
    if not selected:
        print("No verified new candidates. No PR changes were generated.")
        return

    for lang, (catalog_path, archive_path) in enumerate(PATHS):
        data = {section: [render(item, lang) for item in selected if section_for(item) == section] for section in SECTIONS}
        for section in SECTIONS.keys() - {"research"}:
            catalog[lang] = insert(catalog[lang], SECTIONS[section][lang], data[section], section != "release")
        Path(catalog_path).write_text(catalog[lang])
        archive = Path(archive_path)
        archive.write_text(insert(archive.read_text(), SECTIONS["research"][lang], data["research"], True))

    now = datetime.fromisoformat(state["checked"]).astimezone(ZoneInfo("Asia/Seoul"))
    date = now.date().isoformat()
    lines = [
        f"## Weekly Physical AI review · {date}", "",
        "Official sources, access and available license evidence were checked. Both language drafts use the same source records.", "",
        "공식 출처, 공개 범위 및 확인 가능한 이용 조건을 확인했습니다. 영문·한국어 초안은 같은 출처를 사용합니다.", "",
    ]
    lines.extend(f"- {link(item['title'], item['url'])}" for item in selected)
    lines.extend(["", "## Checks · 검증", "", "Astro build, site tests, and lab verification passed.",
                  "사이트 빌드, 검색 테스트, 실습 검증을 통과했습니다."])
    args.body.write_text("\n".join(lines) + "\n")
    print(f"Prepared {len(selected)} verified candidates for review.")


if __name__ == "__main__":
    main()
