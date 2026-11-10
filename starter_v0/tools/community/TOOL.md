---
name: community
track: team
kind: live_api
provider: Hacker News (Algolia), Reddit search RSS, Bluesky public API
requires_env: []
inputs: [query, source, limit]
outputs: [items, errors]
side_effect: false
---
# community

Searches online discussions outside Twitter/X: Hacker News stories, Reddit posts and Bluesky posts. No API key needed.

- `source`: `all` (default), `hackernews`, `reddit` or `bluesky`. Unknown values fall back to `all`.
- `limit`: results per source, clamped to 1-10.
- Each item has `platform`, `title`, `summary`, `url`, `source`, `date`, `metrics`.
- If one source fails (Reddit often rate-limits with 429), the others still return results and the failure is listed in `errors`. If every source fails, the tool returns an error dict.
- Bluesky posts from accounts or posts labelled as adult content are skipped.
