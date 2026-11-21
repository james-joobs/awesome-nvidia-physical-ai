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

from research_queue import (
    canonical_url, marker, marker_ids, pending_records, reconcile_queue,
    record_review, update_queue,
)


GH = "https://github.com"
API = "https://api.github.com"
HF = "https://huggingface.co"
PATHS = (
    ("CATALOG.md", "docs/en/robot-foundation-models.md"),
    ("CATALOG.ko.md", "docs/ko/robot-foundation-models.md"),
)
NVIDIA_OWNERS = {
    "nvidia", "nvlabs", "nvidia-isaac", "nvidia-omniverse",
    "isaac-sim", "nvidia-cosmos", "nvidia-nemo", "nv-tlabs",
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
    (r"alpamayo|autonomous[-_ ]driv|driving[-_ ]world|\bbev\b|alpasim|\bnurec\b", "Autonomous driving and scene reconstruction", "자율주행·장면 재구성"),
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


class ManualVerification(ValueError):
    def __init__(self, message, url):
        super().__init__(message)
        self.url = url


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
        if paper := re.fullmatch(r"/papers/(\d{4}\.\d{4,5})", path):
            return "arxiv:" + paper[1]
        match = re.match(rf"/((?:datasets/)?{NAME}/{NAME})(?:/|$)", path)
        if match:
            return "hub:" + match[1].lower()
    if target.hostname == "arxiv.org":
        match = re.fullmatch(r"/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?", path)
        if match:
            return "arxiv:" + match[1]
    if target.hostname in {"developer.nvidia.com", "research.nvidia.com"}:
        return target.hostname + path.lower()
    return canonical_url(url)


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
        self.resource_links = []
        self.paper_links = []
        self.author_links = []
        self.paper_terms = ""
        self.meta = {}
        self.heading = ""
        self.in_heading = False
        self.in_comments = False
        self.context = []
        self.anchor = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        url = attrs.get("href", "")
        classes = attrs.get("class", "").split()
        context_name = " ".join([attrs.get("id", ""), *classes]).lower()
        blocked = (tag in {"footer", "nav"} or attrs.get("id") in {"footer", "site-footer"}
                   or any(value == "footer" or value.endswith("-footer") for value in classes)
                   or any(value in context_name for value in ("compar", "baseline", "reference", "related")))
        if tag not in {"meta", "link", "br", "hr", "img", "input", "source", "wbr", "area", "base", "embed", "param", "track"}:
            self.context.append((tag, blocked))
        if tag == "a" and attrs.get("title") == "Rights to this article":
            self.paper_terms = re.sub(r"^http://", "https://", url)
        if tag == "a" and url.startswith("https://"):
            self.links.append(url)
            self.anchor = {"url": url, "text": attrs.get("aria-label", "") + " " + attrs.get("title", ""),
                           "blocked": any(value for _, value in self.context)}
            if self.in_comments:
                self.author_links.append(url)
        elif tag == "img" and self.anchor:
            self.anchor["text"] += " " + attrs.get("alt", "")
        elif tag == "td" and "comments" in attrs.get("class", "").split():
            self.in_comments = True
        elif tag == "meta" and attrs.get("name", "").startswith("citation_"):
            self.meta.setdefault(attrs["name"], attrs.get("content", ""))
        elif tag == "h1" and not self.heading:
            self.in_heading = True

    def handle_endtag(self, tag):
        if tag == "a" and self.anchor:
            label = " ".join(self.anchor["text"].split())
            label = label.lstrip("🤗 ")
            if (not self.anchor["blocked"] and re.match(
                    r"^(?:code|source(?:\s+code)?|github|repository|hugging[ -]?face|model(?:\s+weights?)?|weights?|checkpoints?|dataset|data)\b",
                    label, re.I)):
                self.resource_links.append(self.anchor["url"])
            if (not self.anchor["blocked"] and re.match(
                    r"^(?:read(?:\s+the)?\s+paper|paper|arxiv|technical\s+report)\b", label, re.I)
                    and (canonical_url(self.anchor["url"]) or "").startswith("arxiv:")):
                self.paper_links.append(self.anchor["url"])
            self.anchor = None
        if tag == "h1":
            self.in_heading = False
        elif tag == "td":
            self.in_comments = False
        for index in range(len(self.context) - 1, -1, -1):
            if self.context[index][0] == tag:
                del self.context[index:]
                break

    def handle_data(self, data):
        if self.anchor:
            self.anchor["text"] += " " + data
        if self.in_heading:
            # Hero titles often put a project name and subtitle in adjacent
            # spans with no literal whitespace. Preserve text-node boundaries
            # instead of joining "BirdDreams" and "A driving..." into one word.
            self.heading = " ".join((self.heading + " " + data).split())


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
    terms = (license_info.get("license") or {}).get("spdx_id") or "unrecognized"
    path = quote(license_info["path"], safe="/")
    license_url = f"https://raw.githubusercontent.com/{info['full_name']}/{revision}/{path}"
    request(license_url, False)
    if terms not in CODE_LICENSES:
        raise ManualVerification(f"Repository license requires manual review: {terms}", license_url)
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
    terms = (license_info.get("license") or {}).get("spdx_id") or "unrecognized"
    license_url = f"https://raw.githubusercontent.com/{repo}/{tag}/{quote(license_info['path'], safe='/')}"
    request(license_url, False)
    if terms not in CODE_LICENSES:
        raise ManualVerification(f"Release license requires manual review: {terms}", license_url)
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
    card_url = f"{official}/blob/{info['sha']}/README.md"
    license_url = f"{official}/blob/{info['sha']}/{license_file}" if license_file else card_url
    request(license_url, False)
    if not terms:
        value = card.get("license") or "unverified"
        raise ManualVerification(f"Model/dataset license requires manual review: {value}", license_url)
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


def candidates(state, known, queue=None):
    selected = []
    limits = {"repo": 3, "release": 4, "model": 3, "dataset": 3, "research": 4}
    counts = dict.fromkeys(limits, 0)
    selected_keys = set()
    checked = state["checked"]
    items = pending_records(queue, checked) if queue is not None else sorted(
        state["recent"], key=lambda item: item["date"], reverse=True)

    def add(record, item):
        if not record:
            return False
        kind, key = record["kind"], url_key(record["url"])
        if (not key or (key in known and not item.get("_update"))
                or (kind, key) in selected_keys or counts[kind] >= limits[kind]):
            return False
        record.update({field: value for field, value in item.items() if field.startswith("_")})
        record["provenance"] = {
            "discovery_source": item.get("source", "unspecified"),
            "discovery_url": item["url"], "checked": checked,
            "related_urls": item.get("_urls", [item["url"]]),
        }
        counts[kind] += 1
        selected_keys.add((kind, key))
        selected.append(record)
        return True

    def attempt(check, *args):
        try:
            return check(*args)
        except (URLError, OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            print(f"Needs manual verification: {type(error).__name__}")
            reason = str(error) if isinstance(error, ManualVerification) else (
                f"Source verification failed: HTTP {error.code}" if hasattr(error, "code")
                else f"Source verification failed: {type(error).__name__}")
            source = getattr(error, "url", None) or (args[0] if args and str(args[0]).startswith("https://") else item["url"])
            diagnostics.append({"message": reason, "url": source, "checked": checked})

    tried_repos = set()
    attempts = dict.fromkeys(limits, 0)
    for item in items:
        # A larger initial backfill must not exhaust the workflow timeout. The
        # unattempted tail remains pending, rather than aging out after 7 days.
        if sum(attempts.values()) >= 36 or all(counts[kind] >= limits[kind] for kind in limits):
            break
        url = item["url"]
        key = url_key(url) or ""
        update = item.get("_update", False)
        added = False
        attempted = False
        diagnostics = []
        seed_kind = ("release" if key.startswith("release:") else "repo" if key.startswith("github:")
                     else "dataset" if key.startswith("hub:datasets/") else "model" if key.startswith("hub:")
                     else "research")
        if attempts[seed_kind] >= limits[seed_kind] * 3:
            continue
        if key.startswith("release:"):
            if counts["release"] >= limits["release"]:
                continue
            attempted = True
            added = add(attempt(verify_release, url), item)
        elif key.startswith("github:"):
            if counts["repo"] >= limits["repo"]:
                continue
            attempted = True
            repo = key.removeprefix("github:")
            added = add(attempt(verify_repo, repo), item)
        elif key.startswith("hub:"):
            kind = "dataset" if key.startswith("hub:datasets/") else "model"
            if counts[kind] >= limits[kind]:
                continue
            attempted = True
            added = add(attempt(verify_hub, url), item)
        elif key.startswith(("arxiv:", "developer.nvidia.com", "research.nvidia.com")):
            official = key.startswith(("developer.nvidia.com", "research.nvidia.com"))
            if not official and counts["research"] >= limits["research"]:
                continue
            attempted = True
            page = attempt(lambda address: Page(request(address, False)), url)
            if page:
                if (not key.startswith("developer.nvidia.com") and counts["research"] < limits["research"]
                        and (key not in known or update)):
                    study = verify_research(item, page)
                    if study:
                        paper_keys = [value for value in item.get("_aliases", []) if value.startswith("arxiv:")]
                        if not paper_keys:
                            paper_keys = sorted({canonical_url(value) for value in page.paper_links})
                        if not study["paper"] and len(paper_keys) == 1:
                            paper_url = "https://arxiv.org/abs/" + paper_keys[0].removeprefix("arxiv:")
                            paper_page = attempt(lambda address: Page(request(address, False)), paper_url)
                            paper = verify_research({"url": paper_url}, paper_page) if paper_page else None
                            brand = re.sub(r"^NVIDIA\s+", "", study["title"], flags=re.I).split(":")[0].split()[0]
                            same_title = paper and len(brand) >= 4 and re.search(rf"\b{re.escape(brand)}\b", paper["title"], re.I)
                            declared_id = paper_page.meta.get("citation_arxiv_id", "").removeprefix("arXiv:") if paper_page else ""
                            same_id = not declared_id or canonical_url("https://arxiv.org/abs/" + declared_id) == paper_keys[0]
                            if paper and same_id and same_title:
                                study.update(paper_url=paper_url, paper_terms=paper["terms"])
                        upstreams = list(page.resource_links if official else page.author_links)
                        # An arXiv comment often links a project page rather than
                        # directly linking its subsequently released artifacts.
                        project_pages = [v for v in upstreams if urlsplit(v).hostname == "research.nvidia.com"]
                        if study["paper"]:
                            project_pages.extend(v for v in item.get("_urls", [])
                                                 if urlsplit(v).hostname == "research.nvidia.com")
                        for project_url in list(dict.fromkeys(project_pages))[:2]:
                            linked_page = attempt(lambda address: Page(request(address, False)), project_url)
                            own_paper = linked_page and key in {canonical_url(value) for value in linked_page.paper_links}
                            brand = re.sub(r"^NVIDIA\s+", "", study["title"], flags=re.I).split(":")[0].split()[0]
                            own_title = linked_page and len(brand) >= 4 and re.search(
                                rf"\b{re.escape(brand)}\b", linked_page.heading, re.I)
                            if own_paper and own_title:
                                study["project_url"] = project_url
                                upstreams.extend(linked_page.resource_links)
                        for upstream in dict.fromkeys(upstreams):
                            evidence = attempt(author_artifact, upstream)
                            if evidence:
                                study["evidence"].append(evidence)
                            if len(study["evidence"]) >= 3:
                                break
                        added = add(study, item) or added
                if official:
                    for upstream in page.resource_links:
                        repo = re.fullmatch(rf"/({NAME}/{NAME})/?", urlsplit(upstream).path)
                        repo_key = url_key(upstream)
                        if counts["repo"] >= limits["repo"]:
                            break
                        if (urlsplit(upstream).hostname == "github.com" and repo
                                and repo_key not in tried_repos
                                and (repo_key not in known or update)
                                and repo[1].split("/")[0].lower() in NVIDIA_OWNERS):
                            tried_repos.add(repo_key)
                            added = add(attempt(verify_repo, repo[1]), item) or added
        if queue is not None and attempted:
            if added:
                record_review(queue, item, "proposed", checked)
            else:
                record_review(queue, item, "deferred", checked,
                              diagnostics[0]["message"] if diagnostics else
                              "Official source/access/license verification incomplete or unsupported; retry in 7 days")
            if diagnostics:
                for eid in item.get("_event_ids", []):
                    queue["events"][eid]["verification_notes"] = diagnostics
        if attempted:
            attempts[seed_kind] += 1
    return selected


def _render(record, lang):
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
        if record.get("paper_url"):
            cc = re.fullmatch(r"https://creativecommons.org/licenses/([a-z-]+)/([\d.]+)/?", record["paper_terms"])
            license_name = f"CC {cc[1].upper()} {cc[2]}" if cc else ("arXiv 배포 약관" if ko else "arXiv distribution terms")
            publication += " · " + link("논문" if ko else "Paper", record["paper_url"])
            publication += " · " + link(license_name + (" (논문)" if ko else " (paper)"), record["paper_terms"])
    if record.get("project_url") and url_key(record["project_url"]) != url_key(url):
        publication += " · " + link("프로젝트 페이지" if ko else "Project page", record["project_url"])
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


def render(record, lang):
    text = _render(record, lang)
    if record.get("_event_ids"):
        note = marker(record["_event_ids"])
        return text[:-1] + " " + note + " |" if text.endswith("|") else text + " " + note
    return text


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


def matching_rows(text, section, record, table):
    keys = {url_key(record["url"])}
    if record["kind"] == "research":
        keys.update(record.get("_aliases", []))
    start = text.index(section + "\n") + len(section) + 1
    level = len(section) - len(section.lstrip("#"))
    boundary = re.search(rf"^#{{1,{level}}} ", text[start:], re.M)
    end = start + boundary.start() if boundary else len(text)
    matches = [(start + match.start(), start + match.end(), match[0])
               for match in re.finditer(r"^.+$", text[start:end], re.M)
               if keys & seen_urls([match[0]])
               and (match[0].startswith("|") if table else match[0].startswith("- "))]
    return matches


def protect_curated_updates(selected, texts, queue, checked):
    """Hold an entire event if either locale contains a curated matching row.

    Automatic records are deliberately less detailed than hand-written catalog
    entries. Replacing an unowned row could discard asset licenses, access
    caveats, official links and lab guides. Keep its bytes and surface evidence
    for a human instead of guessing a safe field-level edit.
    """
    blocked_ids, blocked_records = set(), set()
    for record in selected:
        if not record.get("_update"):
            continue
        section = section_for(record)
        for lang, paths in enumerate(PATHS):
            path = paths[1] if section == "research" else paths[0]
            try:
                matches = matching_rows(texts[path], SECTIONS[section][lang], record, section != "release")
                unowned = len(matches) > 1 or any(not marker_ids([line]) for _, _, line in matches)
            except (ValueError, KeyError):
                unowned = True
            if unowned:
                blocked_ids.update(record.get("_event_ids", []))
                blocked_records.add((record["kind"], record["url"]))
                reason = f"Manual review required: preserve curated notes and links in {path}"
                record_review(queue, record, "deferred", checked, reason)
                note_url = record.get("license") or record.get("paper_url") or record["url"]
                description = (f"Verified current {record['kind']} terms: {record['terms']}"
                               if record.get("terms") else "Verified upstream source; curated entry retained")
                for eid in record.get("_event_ids", []):
                    queue["events"][eid]["verification_notes"] = [
                        {"message": description, "url": note_url, "checked": checked},
                    ]
                break
    kept = []
    for record in selected:
        if (blocked_ids & set(record.get("_event_ids", []))
                or (record["kind"], record["url"]) in blocked_records):
            # One research page can yield both a research and a repo edit. Do
            # not mark the shared event proposed through an unrelated sibling.
            for eid in record.get("_event_ids", []):
                if queue["events"][eid]["status"] != "deferred":
                    record_review(queue, {"_event_ids": [eid]}, "deferred", checked,
                                  "Manual review required for this project update")
        else:
            kept.append(record)
    return kept


def upsert(text, section, records, lang, table):
    """Update only automation-owned rows; preserve manually curated content."""
    additions = []
    for record in records:
        rendered = render(record, lang)
        if not record.get("_update"):
            additions.append(rendered)
            continue
        matches = matching_rows(text, section, record, table)
        if len(matches) > 1:
            raise ValueError("Multiple existing rows match one updated project; manual review required")
        if matches:
            start, end, line = matches[0]
            if not marker_ids([line]):
                raise ManualVerification("Manual review required: existing row contains curated content", record["url"])
            text = text[:start] + rendered + text[end:]
        else:
            additions.append(rendered)
    return insert(text, section, additions, table)


def backlog_lines(queue):
    statuses = {}
    for event in queue["events"].values():
        statuses[event["status"]] = statuses.get(event["status"], 0) + 1
    lines = ["## Backlog · 누적 대기열", "",
             ", ".join(f"{key}: {value}" for key, value in sorted(statuses.items())) or "0 candidates", "",
             "Unselected candidates remain queued. Deferred items are checked again after seven days.",
             "미선정 후보는 대기열에 보존하며, 확인이 보류된 항목은 7일 뒤 다시 확인합니다."]
    deferred = sorted((event for event in queue["events"].values() if event["status"] == "deferred"),
                      key=lambda event: event.get("reviewed_at", ""), reverse=True)
    if deferred:
        lines.extend(["", "### Manual checks · 추가 확인 필요", ""])
        shown = set()
        for event in deferred:
            if event["project_id"] in shown:
                continue
            if len(shown) >= 20:
                break
            shown.add(event["project_id"])
            record = event["record"]
            lines.append(f"- {link(record['title'], record['url'])} · {clean(event['reason'])}")
            for note in event.get("verification_notes", []):
                lines.append(f"  Evidence / 근거: {link(note['message'], note['url'])}")
    return lines


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--pending", type=Path, required=True)
    parser.add_argument("--body", type=Path, required=True)
    parser.add_argument("--review-state", type=Path,
                        help="Decision overlay, persisted only after a successful scheduled review")
    args = parser.parse_args()
    state = json.loads(args.state.read_text())
    catalog = [Path(pair[0]).read_text() for pair in PATHS]
    guides = [p.read_text() for p in Path("docs").glob("*/*.md")]
    pending = [p.read_text() for p in args.pending.glob("*.md")]
    reviews_path = args.pending / "reviews.json"
    reviews = json.loads(reviews_path.read_text()) if reviews_path.is_file() else []
    queue = state.get("queue") or update_queue({}, state.get("recent", []), state["checked"])
    reconcile_queue(queue, catalog + guides, pending, reviews, state["checked"])
    existing = seen_urls(catalog + guides + pending)
    selected = candidates(state, existing, queue)
    if selected:
        texts = {path: (catalog[lang] if index == 0 else Path(path).read_text())
                 for lang, paths in enumerate(PATHS) for index, path in enumerate(paths)}
        selected = protect_curated_updates(selected, texts, queue, state["checked"])
    review_state = args.review_state or args.body.with_name("review-state.json")
    review_state.parent.mkdir(parents=True, exist_ok=True)
    review_state.write_text(json.dumps({"version": 1, "checked": state["checked"], "queue": queue},
                                      ensure_ascii=False, indent=2) + "\n")
    if not selected:
        args.body.write_text(
            "## Weekly Physical AI review · 주간 검토\n\n"
            "No verified document changes were selected. Pending and deferred candidates remain in the persistent queue.\n\n"
            "이번 검토에서는 문서에 반영할 변경이 선정되지 않았습니다. 대기·보류 후보와 검토 결과는 누적 대기열에 보존합니다.\n\n"
            + "\n".join(backlog_lines(queue)) + "\n")
        print("No verified new candidates. No PR changes were generated.")
        return

    for lang, (catalog_path, archive_path) in enumerate(PATHS):
        data = {section: [item for item in selected if section_for(item) == section] for section in SECTIONS}
        for section in SECTIONS.keys() - {"research"}:
            catalog[lang] = upsert(catalog[lang], SECTIONS[section][lang], data[section], lang, section != "release")
        Path(catalog_path).write_text(catalog[lang])
        archive = Path(archive_path)
        archive.write_text(upsert(archive.read_text(), SECTIONS["research"][lang], data["research"], lang, True))

    now = datetime.fromisoformat(state["checked"]).astimezone(ZoneInfo("Asia/Seoul"))
    date = now.date().isoformat()
    lines = [
        f"## Weekly Physical AI review · {date}", "",
        "Official sources, access and available license evidence were checked. Both language drafts use the same source records.", "",
        "공식 출처, 공개 범위 및 확인 가능한 이용 조건을 확인했습니다. 영문·한국어 초안은 같은 출처를 사용합니다.", "",
    ]
    lines.extend(f"- {link(item['title'], item['url'])} · {'Update / 변경' if item.get('_update') else 'New / 신규'}"
                 for item in selected)
    lines.extend(["", marker(eid for item in selected for eid in item.get("_event_ids", [])), "",
                  "## Evidence · 확인 근거", ""])
    for item in selected:
        evidence = item["provenance"]
        lines.append(f"- {link(item['title'], evidence['discovery_url'])} · "
                     f"{clean(evidence['discovery_source'])} · checked {evidence['checked']}")
    lines.extend(["", *backlog_lines(queue), "", "## Checks · 검증", "",
                  "The workflow runs the site build, site tests and lab verification before opening this PR.",
                  "워크플로는 PR을 열기 전에 사이트 빌드, 검색 테스트, 실습 검증을 실행합니다."])
    args.body.write_text("\n".join(lines) + "\n")
    print(f"Prepared {len(selected)} verified candidates for review.")


if __name__ == "__main__":
    main()
