#!/usr/bin/env python3
"""Collect release, artifact, and paper candidates for editorial review."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from html import escape
from html.parser import HTMLParser
from email.utils import parsedate_to_datetime
import hashlib
import json
import os
from pathlib import Path
import re
from time import sleep
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

from research_queue import update_queue


KST = ZoneInfo("Asia/Seoul")
RECENT_DAYS = 7
RETENTION_DAYS = 45
BACKFILL_DAYS = 90
MAX_PAGES = 5
MAX_BYTES = 8 * 1024 * 1024
GITHUB = "https://api.github.com"
HUB = "https://huggingface.co"
WATCHED = (
    "isaac-sim/IsaacSim", "isaac-sim/IsaacLab", "newton-physics/newton", "NVIDIA/warp",
    "NVIDIA/Isaac-GR00T", "NVIDIA/cosmos", "NVIDIA/cosmos-framework", "NVlabs/alpasim",
    "NVlabs/alpamayo2", "NVlabs/alpamayo2-edge", "NVlabs/RoboLab",
    "black-forest-labs/flux-action", "runwayml/praxis-1-oss", "mimic-video/mimic-video",
)
ORGS = ("NVIDIA", "NVlabs", "isaac-sim", "NVIDIA-Omniverse", "NVIDIA-NeMo", "nvidia-cosmos", "nv-tlabs")
RELATED = re.compile(
    r"robot|isaac|gr00t|cosmos|alpamayo|alpasim|nurec|physical.?ai|omniverse|"
    r"world[- ](?:action|model|simulat)|video[- ]action|manipulat|dexter|"
    r"autonomous[- ]driv|driving[- ]world|sim[- ]to[- ]real|splatting|digital[- ]twin|"
    r"scene[- ]generat|neural[- ]render|\bbev\b|bird.s.eye|ego[- ](?:motion|centric|trajectory)",
    re.I,
)
PAPER_QUERY = (
    '(cat:cs.RO OR cat:cs.CV OR cat:cs.LG) AND ('
    'abs:"world action model" OR abs:"video action model" OR abs:"vision language action" OR '
    'abs:"driving world model" OR abs:"robot world model" OR abs:"video world model" OR '
    'abs:"scene generation" OR abs:"Gaussian splatting" OR abs:"Isaac Lab" OR '
    'abs:"Cosmos" OR abs:"GR00T")'
)


class SourceLimit(ValueError):
    """A bounded source scan found more results; do not advance its watermark."""

    def __init__(self, message, continuation=None, reason="PaginationLimit"):
        super().__init__(message)
        self.continuation = continuation
        self.reason = reason


def allowed_url(url, hosts=None):
    target = urlsplit(url)
    return target.scheme == "https" and target.hostname in (hosts or {
        "api.github.com", "github.com", "huggingface.co", "developer.nvidia.com",
        "research.nvidia.com", "arxiv.org", "export.arxiv.org",
    }) and not target.username and not target.password


def failure_reason(error):
    return f"HTTP {error.code}" if isinstance(error, HTTPError) else type(error).__name__


def instant(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return (parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)).astimezone(UTC)


def fetch(url, json_response=True, with_headers=False):
    if not allowed_url(url):
        raise ValueError("unexpected fetch URL")
    headers = {"User-Agent": "awesome-nvidia-physical-ai-research/1.0"}
    if url.startswith(GITHUB + "/"):
        headers["Accept"] = "application/vnd.github+json"
        token = os.environ.get("GH_TOKEN")
        if token:
            headers["Authorization"] = "Bearer " + token
    for attempt in range(2):
        try:
            with urlopen(Request(url, headers=headers), timeout=15) as response:
                if not allowed_url(response.geturl()):
                    raise ValueError("unexpected source redirect")
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ValueError("response exceeds size limit")
                if json_response == "text":
                    parsed = data.decode("utf-8")
                else:
                    parsed = json.loads(data) if json_response else ElementTree.fromstring(data)
                return (parsed, dict(response.headers)) if with_headers else parsed
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


def entry(key, title, url, date, detail, revision="", **metadata):
    target = urlsplit(url)
    if target.scheme != "https" or target.hostname not in {
        "github.com", "huggingface.co", "developer.nvidia.com", "research.nvidia.com", "arxiv.org",
    }:
        raise ValueError("unexpected source URL")
    url = quote(url, safe=":/?&=%#@+.,;_-~")
    return {
        "id": str(key), "title": title, "url": url, "date": instant(date).isoformat(),
        "detail": detail, "revision": revision, **metadata,
    }


def pagination_target(url, initial):
    target, origin = urlsplit(url), urlsplit(initial)
    if not allowed_url(url) or target.hostname != origin.hostname:
        return False
    if target.path == origin.path:
        return True
    # GitHub release pagination canonicalizes a named repository endpoint to
    # its immutable numeric ID, even when the initial request did not redirect.
    return (origin.hostname == "api.github.com"
            and bool(re.fullmatch(r"/repos/[^/]+/[^/]+/releases", origin.path))
            and bool(re.fullmatch(r"/repositories/\d+/releases", target.path)))


def paged(url, page_size=100, continuation=None):
    """Follow API pagination, reporting truncation instead of silent success."""
    initial = url
    if continuation:
        if continuation.get("kind") != "api" or continuation.get("initial_url") != initial:
            raise ValueError("pagination continuation does not match its source")
        url = continuation["next_url"]
        if not pagination_target(url, initial):
            raise ValueError("unexpected pagination continuation URL")
    visited = set()
    for page in range(1, MAX_PAGES + 1):
        if url in visited:
            raise SourceLimit("API pagination did not advance")
        visited.add(url)
        cursor = {"kind": "api", "initial_url": initial, "next_url": url}
        try:
            records, headers = fetch(url, with_headers=True)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            raise SourceLimit("API page interrupted", cursor, failure_reason(error)) from error
        if not isinstance(records, list):
            raise ValueError("expected an API list")
        yield records
        links = headers.get("Link", headers.get("link", ""))
        following = re.search(r'<([^>]+)>;\s*rel="next"', links)
        if not following:
            # GitHub always sends Link for additional pages. HF does too, but
            # a full unpaginated response is treated conservatively.
            if len(records) >= page_size and urlsplit(url).hostname == "huggingface.co":
                raise SourceLimit("full Hub page without a next cursor")
            return
        next_url = following[1]
        if not pagination_target(next_url, initial):
            raise ValueError("unexpected API pagination URL")
        url = next_url
    raise SourceLimit("API pagination limit reached", {"kind": "api", "initial_url": initial, "next_url": url})


def github_releases(repo, cutoff, continuation=None):
    for records in paged(f"{GITHUB}/repos/{repo}/releases?per_page=100", continuation=continuation):
        for item in records:
            published = item.get("published_at")
            updated = item.get("updated_at") or published
            if item["draft"] or not published or max(instant(published), instant(updated)) < cutoff:
                continue
            label = "프리릴리스" if item["prerelease"] else "릴리스"
            yield entry(item["id"], f"{repo} · {item['tag_name']}", item["html_url"],
                        max(instant(published), instant(updated)).isoformat(), label, item["tag_name"],
                        published_at=published, updated_at=updated, source_kind="release")


def github_repos(org, cutoff, continuation=None):
    url = f"{GITHUB}/orgs/{org}/repos?type=public&sort=created&direction=desc&per_page=100"
    for records in paged(url, continuation=continuation):
        for item in records:
            if instant(item["created_at"]) < cutoff:
                return
            if item["fork"]:
                continue
            if RELATED.search(f"{item['name']} {item.get('description') or ''}"):
                license_id = (item.get("license") or {}).get("spdx_id") or "미확인"
                yield entry(item["id"], item["full_name"], item["html_url"], item["created_at"],
                            f"신규 저장소 · GitHub 라이선스 표기 {license_id}",
                            published_at=item["created_at"], source_kind="repo")


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
                f"GitHub 라이선스 표기 {license_id}", item["sha"],
                source_kind="license", license_id=license_id, license_url=item["html_url"])


def hub_items(kind, author, search, cutoff, continuation=None):
    params = [("author", author), ("limit", 100), ("sort", "lastModified")]
    if search:
        params.append(("search", search))
    params += [("expand[]", field) for field in ("sha", "gated", "cardData", "lastModified")]
    for records in paged(f"{HUB}/api/{kind}?{urlencode(params)}", continuation=continuation):
        for item in records:
            updated = item["lastModified"]
            if instant(updated) < cutoff:
                return
            card = item.get("cardData") or {}
            # Collect the official owner's changed artifacts before topical
            # review. Unknown family names must not be discarded at discovery.
            terms = card.get("license") or "미확인"
            gated = item.get("gated")
            if gated in {"auto", "manual", True}:
                access = "접근 절차 필요"
            elif gated is False:
                access = "접근 제한 표시 없음"
            else:
                access = "접근 상태 미확인"
            prefix = "datasets/" if kind == "datasets" else ""
            yield entry(item["id"], item["id"], f"{HUB}/{prefix}{item['id']}", updated,
                        f"{access} · 모델/데이터 카드 라이선스 {terms}", item.get("sha") or "",
                        updated_at=updated, source_kind=kind, access=access, license_id=terms)


def xml_text(node, name):
    return node.findtext(f"{{*}}{name}", "").strip()


def nvidia_blog(cutoff, continuation=None):
    url = "https://developer.nvidia.com/blog/feed/"
    seen = set()
    first_page = int(continuation["page"]) if continuation else 1
    for page in range(first_page, first_page + MAX_PAGES):
        try:
            nodes = fetch(url + (f"?paged={page}" if page > 1 else ""), False).findall("{*}entry")
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ElementTree.ParseError) as error:
            raise SourceLimit("NVIDIA Atom page interrupted", {"kind": "blog", "page": page}, failure_reason(error)) from error
        if not nodes:
            if page == 1:
                raise ValueError("NVIDIA Atom contains no entries")
            return
        new = 0
        for node in nodes:
            link = node.find("{*}link[@rel='alternate']")
            updated = xml_text(node, "updated") or xml_text(node, "published")
            key = xml_text(node, "id")
            if key in seen:
                continue
            seen.add(key)
            new += 1
            if updated and instant(updated) < cutoff:
                return
            text = " ".join(node.itertext())
            if link is not None and updated and RELATED.search(text):
                yield entry(key or link.attrib["href"], xml_text(node, "title"),
                            link.attrib["href"], updated, "NVIDIA 기술 블로그 · 피지컬 AI 관련 글",
                            updated_at=updated, source_kind="official_blog")
        if len(nodes) < 100:
            return
        if not new:
            raise SourceLimit("NVIDIA Atom pagination did not advance")
    raise SourceLimit("NVIDIA Atom pagination limit reached", {"kind": "blog", "page": first_page + MAX_PAGES})


def nvidia_research(cutoff):
    root = fetch("https://research.nvidia.com/sitemap.xml", False)
    for node in root.findall("{*}url"):
        link = xml_text(node, "loc")
        updated = xml_text(node, "lastmod")
        slug = urlsplit(link).path
        # Project names and URL slugs need not contain our vocabulary. Discover
        # recent official publications first; topical review inspects the page.
        if slug.startswith(("/publication/", "/labs/")) and updated and instant(updated) >= cutoff:
            title = re.sub(r"^\d{4}-\d{2}_", "", slug.rsplit("/", 1)[-1]).replace("-", " ")
            yield entry(link, title, link, updated, "NVIDIA Research · 사이트맵 수정일",
                        source_kind="official_research", updated_at=updated, date_kind="modified")


def arxiv_papers(cutoff, continuation=None):
    start = int(continuation["start"]) if continuation else 0
    for page in range(MAX_PAGES):
        if page:
            sleep(3)  # arXiv API guidance: leave at least three seconds between requests.
        params = {"search_query": PAPER_QUERY, "max_results": 100, "start": start + page * 100,
                  "sortBy": "lastUpdatedDate", "sortOrder": "descending"}
        try:
            root = fetch(f"https://export.arxiv.org/api/query?{urlencode(params)}", False)
            if root.tag != "{http://www.w3.org/2005/Atom}feed":
                raise ValueError("unexpected arXiv response root")
            nodes = root.findall("{*}entry")
            if any("api/errors" in xml_text(node, "id") for node in nodes):
                raise ValueError("arXiv returned an API error entry")
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ElementTree.ParseError) as error:
            raise SourceLimit("arXiv page interrupted", {"kind": "arxiv", "start": start + page * 100}, failure_reason(error)) from error
        for node in nodes:
            updated = xml_text(node, "updated")
            if updated and instant(updated) < cutoff:
                return
            match = re.fullmatch(r"https?://arxiv.org/abs/(\d{4}\.\d{4,5})(v\d+)?", xml_text(node, "id"))
            if match and updated:
                paper, version = match.groups()
                yield entry(paper, xml_text(node, "title"), f"https://arxiv.org/abs/{paper}",
                            updated, "arXiv 프리프린트 · 소속·공개 범위는 원문에서 확인", version or "",
                            paper_id=paper, source_kind="paper", published_at=xml_text(node, "published") or None,
                            updated_at=updated, related_urls=[f"https://arxiv.org/abs/{paper}"])
        if len(nodes) < 100:
            return
    raise SourceLimit("arXiv pagination limit reached", {"kind": "arxiv", "start": start + MAX_PAGES * 100})


class ResearchHTML(HTMLParser):
    """Read links and script URLs without executing third-party JavaScript."""

    def __init__(self, text):
        super().__init__()
        self.links = []
        self.scripts = []
        self.frames = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])
        elif tag == "iframe" and attrs.get("src"):
            self.frames.append(attrs["src"])


class ProjectHTML(ResearchHTML):
    """Read explicit resource buttons outside navigation/comparison templates."""

    def __init__(self, text):
        self.scopes = []
        self.anchor = None
        self.resource_links = []
        self.heading = ""
        self.in_heading = False
        super().__init__(text)

    def handle_starttag(self, tag, attrs):
        super().handle_starttag(tag, attrs)
        values = dict(attrs)
        if tag in {"section", "div", "footer", "nav", "aside"}:
            labels = " ".join((tag, values.get("id", ""), values.get("class", "")))
            blocked = bool(re.search(r"footer|navbar|\bnav\b|compar|baseline|reference|acknowledg|related", labels, re.I))
            self.scopes.append((tag, blocked))
        if tag == "h1" and not self.heading:
            self.in_heading = True
        if tag == "a" and values.get("href") and not any(block for _, block in self.scopes):
            self.anchor = [values["href"], ""]

    def handle_endtag(self, tag):
        if tag == "h1":
            self.in_heading = False
        if tag == "a" and self.anchor:
            self.resource_links.append(tuple(self.anchor))
            self.anchor = None
        if tag in {"section", "div", "footer", "nav", "aside"}:
            for index in range(len(self.scopes) - 1, -1, -1):
                if self.scopes[index][0] == tag:
                    del self.scopes[index:]
                    break

    def handle_data(self, text):
        if self.in_heading:
            self.heading += text
        if self.anchor:
            self.anchor[1] += text


def official_project(url, paper_id, known_artifacts, _cutoff):
    if not allowed_url(url, {"research.nvidia.com"}) or not urlsplit(url).path.startswith("/labs/"):
        raise ValueError("unexpected watched project URL")
    page = ProjectHTML(fetch(url, "text"))
    title = " ".join(page.heading.split())
    if not title:
        raise ValueError("watched project has no heading")
    if paper_id and not any(paper_id in link for link in page.links):
        raise ValueError("watched project's known paper link disappeared")
    code, models, datasets = set(), set(), set()
    for href, text in page.resource_links:
        link = urljoin(url, href)
        label = " ".join(text.split()).strip().lower()
        if not allowed_url(link, {"github.com", "huggingface.co"}):
            continue
        target = urlsplit(link)
        if target.hostname == "github.com" and re.fullmatch(r"(?:view |get |our |source )?(?:code|github|source code)(?: repository)?", label):
            if re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/.*)?", target.path):
                code.add(link)
        elif target.hostname == "huggingface.co" and re.fullmatch(r"(?:view |get |download |our )?(?:model|models|model weights|weights|checkpoints|hugging face)(?: checkpoints)?", label):
            if re.fullmatch(r"/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/.*)?", target.path):
                models.add(link)
        elif target.hostname == "huggingface.co" and re.fullmatch(r"(?:view |get |download |our )?(?:data|dataset|datasets)", label):
            if target.path.startswith("/datasets/"):
                datasets.add(link)
    artifacts = sorted(code | models | datasets)
    identity = [url] + ([f"https://arxiv.org/abs/{paper_id}"] if paper_id else [])
    revision = hashlib.sha256(json.dumps(artifacts, sort_keys=True).encode()).hexdigest()
    return [entry(url, title, url, "1970-01-01", "NVIDIA 공식 프로젝트 재확인 · 명시된 코드·가중치 배포 버튼", revision,
                  paper_id=paper_id, source_kind="official_project", official_source=url,
                  identity_urls=identity, related_urls=identity, code_urls=sorted(code),
                  model_urls=sorted(models), dataset_urls=sorted(datasets),
                  published_at=None, date_kind="unknown",
                  discovery_eligible=bool(set(artifacts) - set(known_artifacts)),
                  baseline_reason="first project watch snapshot; only new resource links enter review")]


def project_sources(previous):
    queue = previous.get("queue", {})
    projects = queue.get("projects", {})
    events = queue.get("events", {})
    checks = previous.get("project_checks", {})
    candidates = {}
    for pid, project in projects.items():
        history = [event for event in events.values() if event.get("project_id") == pid]
        if not history or all(event.get("status") == "baselined" for event in history):
            continue
        links = {link for event in history for field in ("code_urls", "model_urls", "dataset_urls")
                 for link in event.get("record", {}).get(field, [])}
        paper = pid.removeprefix("arxiv:") if pid.startswith("arxiv:") else None
        for url in project.get("urls", []):
            path = urlsplit(url).path
            if allowed_url(url, {"research.nvidia.com"}) and path.startswith("/labs/") and len(path.strip("/").split("/")) >= 3:
                candidates[url] = (checks.get(url, ""), paper, tuple(sorted(links)))
    # Persisted per-URL attempts make the cap fair even when only today's
    # selected watch sources appear in state['sources'].
    selected = sorted(candidates, key=lambda url: (candidates[url][0], url))[:40]
    for url in selected:
        _, paper, links = candidates[url]
        yield f"NVIDIA 프로젝트 재확인 · {url}", official_project, (url, paper, links)


def js_string(literal):
    """Normalize JS-only escapes in a quoted string for the JSON decoder."""
    output, index = [], 0
    while index < len(literal):
        char = literal[index]
        if char != "\\":
            output.append(char)
            index += 1
            continue
        following = literal[index + 1:index + 2]
        if following == "x" and re.fullmatch(r"[0-9a-fA-F]{2}", literal[index + 2:index + 4]):
            output.append("\\u00" + literal[index + 2:index + 4])
            index += 4
        elif following in {'"', "\\", "/", "b", "f", "n", "r", "t", "u"}:
            output.append(literal[index:index + 2])
            index += 2
        else:
            # The source contains LaTeX such as \em in abstracts. Preserve
            # that data as a literal backslash instead of evaluating JS.
            output.append("\\\\")
            index += 1
    return "".join(output)


def js_array(script, marker):
    """Decode a JSON-like publication array, never evaluate JavaScript."""
    offset = script.index(marker) + len(marker)
    start = script.index("[", offset)
    output, depth, index = [], 0, start
    while index < len(script):
        char = script[index]
        if char == '"':
            end = index + 1
            while end < len(script):
                if script[end] == "\\":
                    end += 2
                    continue
                if script[end] == '"':
                    break
                end += 1
            output.append(js_string(script[index:end + 1]))
            index = end + 1
            continue
        if script.startswith("//", index):
            end = script.find("\n", index)
            index = len(script) if end == -1 else end + 1
            continue
        if script.startswith("/*", index):
            end = script.find("*/", index + 2)
            if end == -1:
                raise ValueError("unterminated publication comment")
            index = end + 2
            continue
        if char == ",":
            end = index + 1
            while end < len(script):
                if script[end].isspace():
                    end += 1
                elif script.startswith("//", end):
                    stop = script.find("\n", end)
                    end = len(script) if stop == -1 else stop + 1
                elif script.startswith("/*", end):
                    stop = script.find("*/", end + 2)
                    if stop == -1:
                        raise ValueError("unterminated publication comment")
                    end = stop + 2
                else:
                    break
            if end < len(script) and script[end] in "}]":
                index += 1
                continue
        output.append(char)
        depth += (char == "[") - (char == "]")
        if depth == 0:
            data = json.loads("".join(output))
            if not isinstance(data, list) or not data:
                raise ValueError("publication array is empty")
            return data
        index += 1
    raise ValueError("unterminated publication array")


def research_record(item, source, mapping):
    title = item.get("title", "").strip()
    links = {kind: urljoin(source, item.get(field) or "")
             for kind, field in mapping.items() if item.get(field)}
    if not title or not links:
        return None
    project, paper = links.get("project", ""), links.get("paper", "")
    canonical = next((url for url in (project, paper, links.get("code", "")) if allowed_url(url)), None)
    if not canonical:
        return None
    date = item.get("releaseDate")
    if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        date = None
    evidence = sorted(set(links.values()))
    revision = hashlib.sha256(json.dumps([title, evidence], ensure_ascii=False).encode()).hexdigest()
    paper_id = re.search(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", paper)
    return entry(canonical, title, canonical, date or "1970-01-01", "NVIDIA 연구실 공식 목록 · 코드·가중치 이용 조건은 별도 확인", revision,
                 published_at=date, date_kind="published" if date else "unknown", source_kind="official_lab",
                 official_source=source, paper_id=paper_id[1] if paper_id else None,
                 publication_label=item.get("publication") or item.get("conference") or "",
                 identity_urls=[value for value in (project, paper) if value],
                 related_urls=[value for value in (project, paper) if value],
                 code_urls=[links["code"]] if links.get("code") else [],
                 model_urls=[links["model"]] if links.get("model") else [],
                 dataset_urls=[links["dataset"]] if links.get("dataset") else [])


def backfill_status(record, cutoff):
    """Keep old snapshots for future link changes without flooding first PRs."""
    if record.get("published_at"):
        eligible = instant(record["published_at"]) >= cutoff
    elif record.get("paper_id"):
        prefix = record["paper_id"].split(".", 1)[0]
        year = int(prefix[:2]) + (1900 if int(prefix[:2]) >= 90 else 2000)
        month = int(prefix[2:])
        record["source_month"] = f"{year:04d}-{month:02d}"
        eligible = record["source_month"] >= cutoff.strftime("%Y-%m")
    else:
        years = re.findall(r"\b(?:19|20)\d{2}\b", record.get("publication_label", ""))
        eligible = not years or max(map(int, years)) >= cutoff.year
    record["discovery_eligible"] = eligible
    if not eligible:
        record["baseline_reason"] = "outside initial backfill; retained to detect later artifact changes"
    return record


def sil_publications(cutoff):
    # The public wrapper loads shared/index.html, then publications/main.html,
    # then this data script. Watching the wrapper alone returns no publications.
    source = "https://research.nvidia.com/labs/sil/publications/"
    content_url = urljoin(source, "main.html")
    page = ResearchHTML(fetch(content_url, "text"))
    scripts = [urljoin(content_url, value) for value in page.scripts if value.endswith("/publications.js")]
    if len(scripts) != 1 or not allowed_url(scripts[0], {"research.nvidia.com"}):
        raise ValueError("SIL publication data script missing or ambiguous")
    data = js_array(fetch(scripts[0], "text"), "const PUBLICATIONS_DATA =")
    count = 0
    for item in data:
        record = research_record(item, source, {"project": "project", "paper": "paper", "code": "code", "model": "model", "dataset": "dataset"})
        if record:
            count += 1
            yield backfill_status(record, cutoff)
    if not count:
        raise ValueError("SIL publication data contains no usable research links")


def gear_publications(cutoff):
    # GEAR's current Next.js page ships publications in a named page chunk;
    # __NEXT_DATA__.pageProps alone is an empty object.
    source = "https://research.nvidia.com/labs/gear/publications/"
    page = ResearchHTML(fetch(source, "text"))
    scripts = [urljoin(source, value) for value in page.scripts
               if re.search(r"/pages/publications-[a-z0-9]+\.js$", value)]
    if len(scripts) != 1 or not allowed_url(scripts[0], {"research.nvidia.com"}):
        raise ValueError("GEAR publication page chunk missing or ambiguous")
    script = fetch(scripts[0], "text")
    records = re.split(r"\{title:", script)[1:]
    count = 0
    # Extract only double-quoted display fields. This deliberately does not
    # execute scripts or parse authors, callback code, or unrelated literals.
    for body in records:
        item = {}
        for key in ("title", "projectLink", "paperLink", "codeLink", "modelsLink", "datasetLink", "releaseDate", "conference"):
            pattern = (r'^\s*("(?:\\.|[^"\\])*")' if key == "title"
                       else rf'\b{key}:("(?:\\.|[^"\\])*")')
            match = re.search(pattern, body)
            if match:
                item[key] = json.loads(js_string(match[1]))
        record = research_record(item, source, {"project": "projectLink", "paper": "paperLink", "code": "codeLink", "model": "modelsLink", "dataset": "datasetLink"})
        if record:
            count += 1
            yield backfill_status(record, cutoff)
    if not count:
        raise ValueError("GEAR publication chunk contains no usable records")


def srl_publications(cutoff):
    source = "https://research.nvidia.com/labs/srl/index.xml"
    nodes = fetch(source, False).findall("./channel/item")
    if not nodes:
        raise ValueError("SRL RSS contains no items")
    for node in nodes:
        title = xml_text(node, "title")
        link = urljoin(source, xml_text(node, "link"))
        if not urlsplit(link).path.startswith(("/labs/srl/publication/", "/labs/srl/post/")):
            continue
        date = xml_text(node, "pubDate")
        published = parsedate_to_datetime(date).astimezone(UTC).isoformat() if date else None
        if published and instant(published) < cutoff:
            continue
        if title and allowed_url(link, {"research.nvidia.com"}):
            yield entry(link, title, link, published or "1970-01-01", "NVIDIA Seattle Robotics Lab 공식 RSS",
                        source_kind="official_lab", official_source=source, published_at=published,
                        reference_urls=[urljoin(source, value) for value in ResearchHTML(xml_text(node, "description")).links
                                        if allowed_url(urljoin(source, value))])


def hf_papers(cutoff, continuation=None):
    # Daily Papers lists are dated independently from arXiv submission dates.
    # Backfill each listing day, so papers first promoted later are discovered.
    latest = None
    if continuation:
        day = datetime.fromisoformat(continuation["next_day"]).date()
    else:
        # The API rejects dates later than its latest published Daily Papers
        # edition (including weekends). Read that edition instead of assuming
        # today's UTC calendar date already has a list.
        latest = fetch(f"{HUB}/api/daily_papers")
        dates = [(item.get("paper") or {}).get("submittedOnDailyAt") for item in latest]
        dates = [instant(value).date() for value in dates if value]
        if not dates:
            raise ValueError("Daily Papers latest edition has no listing dates")
        day = max(dates)
    oldest = cutoff.date()
    seen = set()
    remaining = (day - oldest).days + 1
    for offset in range(min(remaining, BACKFILL_DAYS)):
        listed = day - timedelta(days=offset)
        try:
            items = latest if offset == 0 and latest is not None else fetch(f"{HUB}/api/daily_papers?{urlencode({'date': listed.isoformat()})}")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
            reason = failure_reason(error)
            raise SourceLimit("Daily Papers listing interrupted", {"kind": "hf_papers", "next_day": listed.isoformat()}, reason) from error
        for item in items:
            paper = item.get("paper") or {}
            title = paper.get("title") or item.get("title") or ""
            summary = paper.get("summary") or item.get("summary") or ""
            paper_id = paper.get("id", "")
            if paper_id in seen or not re.fullmatch(r"\d{4}\.\d{4,5}", paper_id) or not RELATED.search(title + " " + summary):
                continue
            seen.add(paper_id)
            # Current list records include projectPage. Use the detail endpoint
            # only for older/partial list shapes, keeping a 90-day backfill to
            # roughly one request per day rather than one request per paper.
            detail = paper
            if "projectPage" not in paper:
                try:
                    detail = fetch(f"{HUB}/api/papers/{paper_id}")
                except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
                    reason = failure_reason(error)
                    raise SourceLimit("Daily Papers detail interrupted", {"kind": "hf_papers", "next_day": listed.isoformat()}, reason) from error
            project = detail.get("projectPage")
            url = f"https://arxiv.org/abs/{paper_id}"
            related = [url, f"{HUB}/papers/{paper_id}"]
            if isinstance(project, str) and project.startswith("https://"):
                related.append(project)
            published = detail.get("publishedAt") or paper.get("publishedAt")
            submitted = detail.get("submittedOnDailyAt") or paper.get("submittedOnDailyAt")
            yield entry(paper_id, title, url, submitted or published or "1970-01-01",
                        "Hugging Face Papers 발견 · 공식 출처·소속·공개 범위는 원문에서 확인",
                        source_kind="paper_discovery", paper_id=paper_id, published_at=published,
                        listed_at=submitted, identity_urls=[url] + ([project] if project else []), related_urls=related)
    if remaining > BACKFILL_DAYS:
        raise SourceLimit("Daily Papers backfill continues", {"kind": "hf_papers", "next_day": (day - timedelta(days=BACKFILL_DAYS)).isoformat()})


def tracked_repos():
    """Include official upstreams already documented, not only family names."""
    repos = {value.lower(): value for value in WATCHED}
    catalog = Path(__file__).resolve().parent.parent / "CATALOG.md"
    if catalog.is_file():
        for owner, name in re.findall(r"https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)", catalog.read_text()):
            if owner.lower() in {org.lower() for org in ORGS} | {"nvidia-isaac", "newton-physics"}:
                name = name.removesuffix(".git")
                repo = f"{owner}/{name}"
                repos.setdefault(repo.lower(), repo)
    return tuple(repos.values())


def sources(previous=None):
    for repo in tracked_repos():
        yield f"GitHub 릴리스 · {repo}", github_releases, (repo,)
        yield f"GitHub 라이선스 · {repo}", github_license, (repo,)
    for org in ORGS:
        yield f"GitHub 신규 저장소 · {org}", github_repos, (org,)
    for kind in ("models", "datasets"):
        yield f"Hugging Face {kind} · nvidia 관련 전체 목록", hub_items, (kind, "nvidia", "")
    for owner, family in (("black-forest-labs", "action"), ("runwayml", "praxis"), ("GEAR-Dreams", "dreamzero")):
        yield f"Hugging Face models · {owner}/{family}", hub_items, ("models", owner, family)
    yield "NVIDIA 기술 블로그 Atom", nvidia_blog, ()
    yield "NVIDIA Research 사이트맵", nvidia_research, ()
    yield "NVIDIA SIL 공식 논문 목록", sil_publications, ()
    yield "NVIDIA GEAR 공식 논문 목록", gear_publications, ()
    yield "NVIDIA Seattle Robotics Lab RSS", srl_publications, ()
    yield "Hugging Face Papers", hf_papers, ()
    yield "arXiv cs.RO·cs.CV·cs.LG", arxiv_papers, ()
    yield from project_sources(previous or {})


def collect(previous, now, inputs):
    states, changes, observations = {}, [], []
    project_checks = dict(previous.get("project_checks", {}))
    baseline = now - timedelta(days=RECENT_DAYS)
    expiry = now - timedelta(days=180)

    def scan(input_source):
        name, query, args = input_source
        saved = previous.get("sources", {}).get(name, {})
        last_success = saved.get("last_success")
        continuation = saved.get("continuation")
        cutoff = (min(baseline, instant(last_success) - timedelta(days=1)) if last_success
                  else now - timedelta(days=BACKFILL_DAYS))
        scan_started = now.isoformat()
        if continuation:
            cutoff = instant(continuation["cutoff"])
            scan_started = continuation["scan_started"]
        known = {key: value for key, value in saved.get("items", {}).items()
                 if instant(value["date"]) >= expiry or value["date"].startswith("1970-")}
        records, error = [], None
        try:
            for record in query(*args, cutoff, **({"continuation": continuation} if continuation else {})):
                records.append(record)
        except SourceLimit as limit:
            error = limit.reason
            continuation = ({**limit.continuation, "cutoff": cutoff.isoformat(), "scan_started": scan_started}
                            if limit.continuation else None)
        except (OSError, ValueError, KeyError, TypeError, AttributeError, ElementTree.ParseError) as error:
            reason = failure_reason(error)
            return name, saved, known, records, reason, continuation, scan_started
        else:
            continuation = None
        return name, saved, known, records, error, continuation, scan_started

    # Network calls dominate collection. Each source retains its own watermark,
    # and six workers keep catalog-derived upstream coverage within the job's
    # time budget without a burst of hundreds of concurrent requests.
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(scan, inputs))
    for name, saved, known, records, error, continuation, scan_started in results:
        if name.startswith("NVIDIA 프로젝트 재확인 · "):
            project_checks[name.split(" · ", 1)[1]] = now.isoformat()
        for record in records:
            observations.append({**record, "source": name})
            key = record["id"]
            old = known.get(key)
            # Sources already enforce their date windows when dates exist.
            # Undated official pages are admitted by first discovery, not by
            # an invented publication date.
            if old != record and (old or record.get("discovery_eligible") is not False):
                changes.append({**record, "source": name, "detected": now.isoformat()})
            known[key] = record
        states[name] = {"last_success": saved.get("last_success") if error else scan_started,
                        "last_attempt": now.isoformat(), "error": error, "items": known,
                        "item_count": len(records)}
        if error:
            states[name]["first_failure"] = saved.get("first_failure") or now.isoformat()
        if continuation:
            states[name]["continuation"] = continuation
        print(f"{'Incomplete' if error else 'Checked'}: {name} ({len(records)})" + (f" · {error}" if error else ""))
    recent = {
        item["url"]: item
        for item in previous.get("recent", []) + changes
        if instant(item["detected"]) >= baseline
    }
    return {
        "checked": now.isoformat(), "sources": states, "recent": list(recent.values()),
        "changes": len({item["url"] for item in changes}),
        "queue": update_queue(previous.get("queue", {}), previous.get("recent", []) + observations, now.isoformat()),
        "project_checks": project_checks,
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
        "아래 항목은 검토 후보입니다. 항목 날짜는 원문의 발표·수정 또는 Papers 등록 시각이며, "
        "최초 발견일과는 구분합니다. 날짜가 없는 목록은 날짜 미제공으로 표시합니다. "
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
    queue = state.get("queue", {})
    events = queue.get("events", {})
    statuses = {}
    waiting = {}
    for event in events.values():
        status = event["status"]
        statuses[status] = statuses.get(status, 0) + 1
        if status not in {"pending", "deferred"}:
            continue
        pid = event["project_id"]
        prior = waiting.get(pid)
        if prior is None or event["first_seen"] < prior["first_seen"]:
            waiting[pid] = event
    lines += ["## 누적 검토 대기열", "",
              f"대기 중인 프로젝트 {len(waiting)}개 · 전체 검토 사건 {len(events)}개", "",
              " · ".join(f"{status}: {statuses.get(status, 0)}" for status in
                         ("pending", "deferred", "proposed", "merged", "rejected")), "",
              "주간 선정 한도를 넘긴 후보도 다음 주에 남습니다. 아래는 가장 오래 기다린 프로젝트 최대 10개입니다.", ""]
    for pid, event in sorted(waiting.items(), key=lambda pair: (pair[1]["first_seen"], pair[0]))[:10]:
        record = event["record"]
        title = queue.get("projects", {}).get(pid, {}).get("title", record["title"])
        url = quote(record["url"], safe=":/?&=%#@+.,;_-~")
        next_check = f" · 재확인 {event['next_check'][:10]}" if event.get("next_check") else ""
        lines.append(f"- [{md_text(title)}]({url}) · {event['status']} · "
                     f"최초 발견 {event['first_seen'][:10]}{next_check}")
    if not waiting:
        lines.append("대기 중인 프로젝트가 없습니다.")
    lines += ["", "## 출처별 상태", "", f"확인 성공 {len(state['sources']) - len(errors)}개 · 실패 또는 조회 진행 중 {len(errors)}개", ""]
    for name, source in state["sources"].items():
        status = source["error"] or "성공"
        progress = " · 다음 실행에서 후속 조회" if source.get("continuation") else ""
        lines.append(f"- {md_text(name)} · {status} · 마지막 성공 {local_time(source['last_success'])}{progress}")
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    previous = json.loads(args.previous.read_text()) if args.previous.is_file() else {}
    state = collect(previous, datetime.now(UTC), sources(previous))
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    (args.output / "latest.md").write_text(report(state))
    if instant(state["checked"]).astimezone(KST).weekday() == 4:
        (args.output / "weekly.md").write_text(report(state))
    print(f"{state['changes']} changed entries")


if __name__ == "__main__":
    main()
