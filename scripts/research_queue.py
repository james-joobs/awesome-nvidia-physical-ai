"""Persistent, event-based review backlog for the research monitor (stdlib only)."""

import argparse
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


MARKER = re.compile(r"<!--\s*research-events?:([a-f0-9, ]+)\s*-->")
DECISION_FIELDS = ("status", "reason", "reviewed_at", "next_check", "proposed_at", "blocked_by_review", "verification_notes")
ACTIVE = {"pending", "deferred"}
NVIDIA_OWNERS = {"nvidia", "nvlabs", "nvidia-isaac", "nvidia-omniverse", "isaac-sim",
                 "nvidia-cosmos", "nvidia-nemo", "nv-tlabs"}


def canonical_url(url):
    """Drop display/version/analytics suffixes without merging different releases."""
    target = urlsplit(str(url))
    host = (target.hostname or "").lower()
    path = unquote(target.path).rstrip("/")
    if host in {"arxiv.org", "export.arxiv.org"}:
        paper = re.fullmatch(r"/(?:abs|pdf)/(\d{4}\.\d{4,5})(?:v\d+)?(?:\.pdf)?", path)
        if paper:
            return "arxiv:" + paper[1]
    if host == "huggingface.co" and (paper := re.fullmatch(r"/papers/(\d{4}\.\d{4,5})", path)):
        return "arxiv:" + paper[1]
    if host in {"github.com", "raw.githubusercontent.com"}:
        parts = path.split("/")
        if len(parts) >= 3:
            repo = "/".join(parts[1:3]).lower().removesuffix(".git")
            if len(parts) >= 6 and parts[3:5] == ["releases", "tag"]:
                return "release:" + repo + "/" + "/".join(parts[5:])
            return "github:" + repo
    if host == "huggingface.co":
        parts = path.split("/")
        n = 4 if len(parts) > 1 and parts[1] == "datasets" else 3
        if len(parts) >= n:
            return "hub:" + "/".join(parts[1:n]).lower()
    if host in {"research.nvidia.com", "developer.nvidia.com"}:
        return host + path.lower()
    return None


def observation_urls(item):
    result = [item.get("url", "")]
    for field in ("identity_urls", "related_urls", "code_urls", "model_urls", "dataset_urls", "artifact_urls"):
        values = item.get(field, [])
        result.extend([values] if isinstance(values, str) else values)
    if item.get("paper_id"):
        result.append("https://arxiv.org/abs/" + item["paper_id"])
    return sorted({v for v in result if isinstance(v, str) and canonical_url(v)})


def identity_keys(item):
    """A common dependency/dataset is an edge, never a shared paper identity."""
    primary = canonical_url(item.get("url", ""))
    keys = {primary} if primary else set()
    identity = item.get("identity_urls", item.get("related_urls", []))
    if isinstance(identity, str):
        identity = [identity]
    # Discovery adapters only identify a paper's own paper/project URLs here.
    # Artifact URLs stay in provenance even when an adapter includes one by
    # mistake. Two papers can legitimately share the same repository or model.
    for url in identity:
        key = canonical_url(url)
        if key and (key.startswith("arxiv:") or key.startswith("research.nvidia.com")):
            keys.add(key)
    if item.get("paper_id"):
        keys.add("arxiv:" + item["paper_id"])
    primary_paper = primary if primary and primary.startswith("arxiv:") else None
    authoritative = "arxiv:" + item["paper_id"] if item.get("paper_id") else primary_paper
    if authoritative:
        keys = {key for key in keys if not key.startswith("arxiv:") or key == authoritative}
    elif sum(key.startswith("arxiv:") for key in keys) > 1:
        keys = {key for key in keys if not key.startswith("arxiv:")}
    return keys


def semantic_snapshot(item):
    """Poll times and source wording are not release or availability events."""
    key = canonical_url(item.get("url", "")) or ""
    artifact = key.startswith(("github:", "hub:", "release:"))
    data = {"revision": item.get("revision", "")}
    # Legacy collectors encoded Hub access/license and GitHub license in detail.
    if artifact:
        data["detail"] = item.get("detail", "")
    for field in ("license", "license_url", "terms", "access", "gated", "private"):
        if field in item:
            data[field] = item[field]
    data["artifacts"] = sorted({canonical_url(v) for v in observation_urls(item)
                                if (canonical_url(v) or "").startswith(("github:", "hub:"))})
    return data


def _stamp(item, checked):
    return item.get("detected") or item.get("first_seen") or checked


def _event_id(key, snapshot):
    value = json.dumps([key, snapshot], sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(value.encode()).hexdigest()[:24]


def update_queue(previous, observations, checked):
    """Accumulate all unreviewed discoveries; retain decisions across daily scans.

    Project aliases connect paper, lab page and author-linked artifacts. Event IDs
    are based on each observation's canonical URL + semantic state, so a newer
    release/license/access/link change at a known URL is independently reviewable.
    """
    queue = deepcopy(previous or {"version": 1, "projects": {}, "events": {}})
    queue.setdefault("version", 1)
    projects, events = queue.setdefault("projects", {}), queue.setdefault("events", {})
    aliases = {alias: pid for pid, p in projects.items() for alias in p["aliases"]}
    for item in observations:
        key = canonical_url(item.get("url", ""))
        if not key:
            continue
        urls = observation_urls(item)
        keys = identity_keys(item)
        existing = {aliases[v] for v in keys if v in aliases}
        paper_keys = sorted(v for v in keys if v.startswith("arxiv:"))
        pid = paper_keys[0] if paper_keys else (sorted(existing)[0] if existing else key)
        first = _stamp(item, checked)
        project = projects.setdefault(pid, {
            "id": pid, "title": item.get("title", pid), "aliases": [], "urls": [],
            "first_seen": first, "last_seen": checked, "snapshots": {},
        })
        # A later official page can establish that two discoveries are one project.
        for old_id in existing - {pid}:
            if old_id.startswith("arxiv:") and pid.startswith("arxiv:"):
                # A mistaken comparison link must not collapse different papers.
                continue
            old = projects.pop(old_id)
            project["aliases"] = sorted(set(project["aliases"] + old["aliases"]))
            project["urls"] = sorted(set(project["urls"] + old["urls"]))
            project["first_seen"] = min(project["first_seen"], old["first_seen"])
            project.setdefault("snapshots", {}).update(old.get("snapshots", {}))
            for event in events.values():
                if event["project_id"] == old_id:
                    event["project_id"] = pid
        project["aliases"] = sorted(set(project["aliases"]) | keys)
        project["urls"] = sorted(set(project["urls"] + urls))
        project["first_seen"] = min(project["first_seen"], first)
        project["last_seen"] = checked
        for alias in project["aliases"]:
            aliases[alias] = pid
        snapshot = semantic_snapshot(item)
        eid = _event_id(key, snapshot)
        observation_key = key + "|" + item.get("source", "unspecified")
        snapshots = project.setdefault("snapshots", {})
        previous_snapshot = snapshots.get(observation_key)
        snapshots[observation_key] = {"snapshot": snapshot, "last_seen": checked}
        if eid not in events and item.get("discovery_eligible") is False:
            if previous_snapshot is None or previous_snapshot["snapshot"] == snapshot:
                # Keep old publication snapshots so later code/weight changes
                # are detectable, without proposing the entire historical lab.
                continue
        if eid not in events:
            prior = [v for v in events.values() if v["canonical_url"] == key]
            reason = "new discovery"
            if prior:
                before = max(prior, key=lambda v: v["last_seen"])["snapshot"]
                changed = [field for field in sorted(set(before) | set(snapshot))
                           if before.get(field) != snapshot.get(field)]
                reason = "changed: " + ", ".join(changed)
            events[eid] = {
                "id": eid, "project_id": pid, "canonical_url": key,
                "snapshot": snapshot, "record": deepcopy(item), "status": "pending",
                "reason": reason, "change_reason": reason, "first_seen": first, "last_seen": checked,
                "sources": [],
            }
        event = events[eid]
        event["project_id"] = pid
        event["last_seen"] = checked
        event["record"] = deepcopy(item)
        provenance = {"source": item.get("source", "unspecified"), "url": item["url"]}
        if provenance not in event["sources"]:
            event["sources"].append(provenance)
    queue["checked"] = checked
    return queue


def marker_ids(contents):
    return {eid.strip() for text in contents for match in MARKER.findall(text)
            for eid in match.split(",") if eid.strip()}


def marker(ids):
    return "<!-- research-events:" + ",".join(sorted(set(ids))) + " -->"


def reconcile_queue(queue, merged_contents, pending_contents, reviews, checked):
    """Reconcile published markers and PR decisions; legacy links form a baseline."""
    merged_ids = marker_ids(merged_contents)
    pending_ids = marker_ids(pending_contents)
    decisions = {}
    for review in reviews:
        status = "merged" if review.get("mergedAt") or review.get("state") == "MERGED" else (
            "rejected" if review.get("state") == "CLOSED" else "proposed")
        for eid in marker_ids([review.get("body", "")]):
            decisions[eid] = status
    known = {canonical_url(url) for text in merged_contents
             for url in re.findall(r"https://[^\s)\]>]+", text)} - {None}
    pending_urls = {canonical_url(url) for text in pending_contents
                    for url in re.findall(r"https://[^\s)\]>]+", text)} - {None}
    tracked_pending_urls = {canonical_url(url) for text in pending_contents
                            for line in text.splitlines() if marker_ids([line])
                            for url in re.findall(r"https://[^\s)\]>]+", line)} - {None}
    open_ids = pending_ids | {eid for eid, status in decisions.items() if status == "proposed"}
    open_projects = {queue["events"][eid]["project_id"] for eid in open_ids if eid in queue["events"]}
    # Snapshot terminal history before baselining: the first observation is not a
    # retrospective update, but later observations at that URL must be reviewed.
    previously_tracked = {v["canonical_url"] for v in queue["events"].values()
                          if v["status"] in {"merged", "rejected"} and v.get("reviewed_at")}
    tracked_projects = {v["project_id"] for v in queue["events"].values()
                        if v["status"] in {"merged", "rejected"} and v.get("reviewed_at")}
    for eid, event in queue["events"].items():
        if eid in merged_ids:
            status, reason = "merged", "present in main documents"
        elif eid in pending_ids:
            status, reason = "proposed", "present in an open review"
        elif eid in decisions:
            status, reason = decisions[eid], "recorded pull request decision"
        elif event["status"] in {"merged", "rejected"}:
            continue
        elif event["project_id"] in open_projects and eid not in open_ids:
            event.update(status="deferred", reason="awaiting an open review for this project",
                         reviewed_at=checked, blocked_by_review=True,
                         next_check=(datetime.fromisoformat(checked) + timedelta(days=1)).isoformat())
            continue
        elif event.get("blocked_by_review"):
            event.pop("blocked_by_review", None)
            event.pop("next_check", None)
            event.update(status="pending", reason=event.get("change_reason", "changed source"), reviewed_at=checked)
            continue
        elif event["canonical_url"] in pending_urls and event["canonical_url"] not in tracked_pending_urls:
            status, reason = "proposed", "source already included in an open review"
        elif (event["canonical_url"] in known and event["canonical_url"] not in previously_tracked
              and event["project_id"] not in tracked_projects
              and set(event["snapshot"].get("artifacts", [])) <= known):
            # All semantic variants from the initial ingestion become a baseline;
            # otherwise the different feed formats would generate an update PR.
            status, reason = "merged", "baseline: source already linked before event tracking"
        else:
            continue
        event.update(status=status, reason=reason, reviewed_at=checked)
        if status in {"proposed", "merged", "rejected"}:
            event.pop("blocked_by_review", None)
            event.pop("next_check", None)
    return queue


def pending_records(queue, checked):
    """Prioritize official NVIDIA identities, oldest first within each tier."""
    grouped = {}
    for eid, event in queue["events"].items():
        if event["status"] not in ACTIVE or event.get("next_check", "") > checked:
            continue
        grouped.setdefault(event["project_id"], []).append(event)
    result = []
    for pid, events in grouped.items():
        def priority(event):
            record = event["record"]
            key = event["canonical_url"]
            # An official NVIDIA page can expose code/weights that are absent
            # from the original arXiv comments. Prefer it when available.
            return (key.startswith("research.nvidia.com"), key.startswith("arxiv:"), event["last_seen"])
        representative = max(events, key=priority)
        item = deepcopy(representative["record"])
        item["_event_ids"] = [v["id"] for v in events]
        item["_project_id"] = pid
        item["_first_seen"] = min(v["first_seen"] for v in events)
        item["_aliases"] = queue["projects"][pid]["aliases"]
        item["_urls"] = queue["projects"][pid]["urls"]
        item["_update"] = any(v["project_id"] == pid and v["status"] == "merged"
                              for v in queue["events"].values())
        item["_change_reasons"] = sorted({v.get("change_reason", v["reason"]) for v in events})
        result.append(item)
    def official_priority(item):
        for alias in item["_aliases"]:
            if alias.startswith(("research.nvidia.com", "developer.nvidia.com", "hub:nvidia/", "hub:datasets/nvidia/")):
                return True
            if alias.startswith(("github:", "release:")) and alias.split(":", 1)[1].split("/", 1)[0] in NVIDIA_OWNERS:
                return True
        return False
    def source_recency(item):
        value = item.get("updated_at") or item.get("date") or item.get("published_at")
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return -(date if date.tzinfo else date.replace(tzinfo=UTC)).timestamp()
        except (AttributeError, ValueError, OverflowError):
            return 0
    return sorted(result, key=lambda item: (not official_priority(item), item["_first_seen"],
                                           source_recency(item), item["_project_id"]))


def record_review(queue, record, status, checked, reason=""):
    for eid in record.get("_event_ids", []):
        event = queue["events"][eid]
        event.update(status=status, reviewed_at=checked)
        if reason:
            event["reason"] = reason
        if status == "proposed":
            event["proposed_at"] = checked
            event.pop("next_check", None)
        elif status == "deferred":
            event["next_check"] = (datetime.fromisoformat(checked) + timedelta(days=7)).isoformat()


def merge_review_state(state, overlay):
    """Apply decisions only: never overwrite newer observations/source health."""
    result = deepcopy(state)
    queue = result.setdefault("queue", {"version": 1, "projects": {}, "events": {}})
    other = overlay.get("queue", {})
    # Initial upgrade from an old report can introduce its migrated backlog.
    for pid, project in other.get("projects", {}).items():
        queue["projects"].setdefault(pid, deepcopy(project))
    for eid, reviewed in other.get("events", {}).items():
        if eid not in queue["events"]:
            queue["events"][eid] = deepcopy(reviewed)
            continue
        current = queue["events"][eid]
        if reviewed.get("reviewed_at", "") >= current.get("reviewed_at", ""):
            for field in DECISION_FIELDS:
                if field in reviewed:
                    current[field] = deepcopy(reviewed[field])
                elif field in {"next_check", "blocked_by_review"}:
                    current.pop(field, None)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--review-state", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = merge_review_state(json.loads(args.state.read_text()), json.loads(args.review_state.read_text()))
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
