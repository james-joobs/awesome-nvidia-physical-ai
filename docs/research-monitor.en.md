# Physical AI research monitoring

English · [한국어](research-monitor.md)

[Workflow runs](https://github.com/james-joobs/awesome-nvidia-physical-ai/actions/workflows/collect-research.yml) · [Latest report](https://github.com/james-joobs/awesome-nvidia-physical-ai/blob/research-reports/latest.md)

GitHub Actions checks upstream sources daily at 09:17 Asia/Seoul. On Fridays, it verifies queued candidates and prepares a bilingual draft PR. A maintainer reviews and merges the PR before Pages publishes the changes.

## Sources and evidence

The monitor checks releases and licenses for configured repositories and official repositories linked from the catalog; new repositories in related NVIDIA organizations; Hugging Face models, datasets and Papers; NVIDIA technical blogs and the Research sitemap; and research lists from SIL, GEAR and Seattle Robotics Lab. The arXiv query includes relevant work in `cs.RO`, `cs.CV` and `cs.LG`.

New sources look back up to 90 days. Subsequent checks overlap the last successful scan. Paginated lists have explicit bounds; truncation and parser failures are reported as source failures rather than a successful empty scan. Feeds that have dropped older entries cannot provide a complete historical recovery.

Publication and modification dates remain separate from first detection and last observation. A sitemap modification time is not a paper publication date. Undated research lists can still produce a first-seen observation.

Paper, code, weights and dataset availability are checked independently. A paper license is not a code or model license. If an official page has no distribution link, the report records that the official link has not been confirmed. Inclusion in the research archive does not imply that a runnable lab is available.

## Persistent review queue

`research-reports` stores these files:

| File | Purpose |
| --- | --- |
| `latest.md` | Recent discoveries, persistent backlog and source health |
| `weekly.md` | Friday report snapshot |
| `state.json` | Source observations and persistent project/event queue |
| `review-state.json` | Review decisions applied to the next collection without replacing newer observations |

Explicit identity links join a paper's arXiv entry, Hugging Face Papers entry and official project page. Different projects using the same library are not combined. A new revision, license, access condition or artifact link at an existing URL can create a new review event.

| Status | Meaning |
| --- | --- |
| `pending` | A discovery or change not yet proposed |
| `deferred` | Waiting for verification or an existing review; retained for a later check |
| `proposed` | Included in an open review PR |
| `merged` | Published in the documents, or established as an existing baseline |
| `rejected` | A proposal closed without merging; the same event is not proposed again |

Weekly selection limits do not discard overflow candidates. PR event markers reconcile proposals with open, merged and closed reviews. New changes remain eligible after an earlier event was reviewed. Both language drafts use the same verified source records, and missing evidence remains a manual-review reason.

Candidates linked to an official NVIDIA project or an official repository owner are reviewed first, then ordered by waiting time within that priority. Existing curated rows are preserved rather than replaced by generic generated text; changes receive evidence for manual review.

Review decisions are saved only after validation and successful PR creation. In **Run workflow**, enabling **review_preview** produces a `weekly-research-review` artifact containing the patch, PR body and review-state preview. It does not create a PR or finalize review decisions.

To validate collector changes before merging, run `review_preview=true` on the review branch. This checks that branch's code without writing the public report branch, opening a PR or saving review decisions. A preview on `main` still saves the collection report.

## Health and regression checks

A source check includes parsing and pagination, not just an HTTP response. Failed sources retain their previous observations and queue. Individual failures appear in the report and Actions warnings; failures lasting at least three days receive a repair warning. Other verified sources remain eligible. If every source fails, no weekly proposal is made.

Rate limits and per-run pagination bounds preserve partial results and a continuation cursor. Official project-page checks rotate fairly through up to 40 pages per run using persisted check times. If every source fails, the failed report remains available as an Actions artifact and the previously published report branch is preserved.

Scheduled runs can be delayed or dropped. Check both workflow execution times and each source's last successful observation. [GitHub schedule behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

Run the offline regression suite with:

```sh
python3 -m unittest discover -s scripts -p 'test_research*.py'
```

The suite covers research such as BirdDreams in `cs.CV`, lab iframe/data layouts, explicit project identities, and changes to release or access evidence at an existing URL.

## Local report mirror on macOS

After the first report is published, run:

```sh
./scripts/install-macos-research-sync.sh
```

The default checkout is `~/work/awesome-nvidia-physical-ai-reports/`. Pass an absolute directory as the first argument to use another location. The existing login job updates the dedicated checkout at login and at minutes 07 and 37. GitHub keeps collecting while the Mac is off; the next login fetches the latest reports. Avoid editing this checkout, because local changes can prevent a safe fast-forward update. Its log is `~/Library/Logs/physical-ai-research-sync.log`.
