from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from html import unescape
from typing import Any, Callable

import requests

from tools._shared import TIMEOUT, err

# All three are public, keyless endpoints. Reddit's JSON API returns 403 without OAuth, so we use its search RSS.
HEADERS = {"User-Agent": "AI20k-Day03-Research-Agent/1.0 (educational lab)"}
ATOM = {"atom": "http://www.w3.org/2005/Atom"}
ADULT_LABELS = {"porn", "sexual", "nudity", "graphic-media"}


def _hackernews(query: str, limit: int) -> list[dict[str, Any]]:
    response = requests.get(
        "https://hn.algolia.com/api/v1/search",
        params={"query": query, "tags": "story", "hitsPerPage": limit},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    items = []
    for hit in response.json().get("hits", []):
        discussion = f"https://news.ycombinator.com/item?id={hit.get('objectID')}"
        items.append({
            "platform": "hackernews",
            "title": hit.get("title") or "",
            "summary": (hit.get("story_text") or hit.get("title") or "")[:500],
            "url": discussion,
            "link": hit.get("url") or discussion,
            "source": "news.ycombinator.com",
            "date": hit.get("created_at"),
            "metrics": {"points": hit.get("points"), "comments": hit.get("num_comments")},
        })
    return items


def _reddit(query: str, limit: int) -> list[dict[str, Any]]:
    response = requests.get(
        "https://www.reddit.com/search.rss",
        params={"q": query, "limit": limit, "sort": "relevance", "t": "month"},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    items = []
    for entry in ET.fromstring(response.text).findall("atom:entry", ATOM):
        link = entry.find("atom:link", ATOM)
        category = entry.find("atom:category", ATOM)
        content = unescape(re.sub(r"<[^>]+>", " ", entry.findtext("atom:content", "", ATOM)))
        items.append({
            "platform": "reddit",
            "title": entry.findtext("atom:title", "", ATOM).strip(),
            "summary": " ".join(content.split())[:500],
            "url": link.get("href") if link is not None else "",
            "source": category.get("label") if category is not None else "reddit.com",
            "date": entry.findtext("atom:updated", None, ATOM),
            "metrics": {},
        })
    return items[:limit]


def _bluesky(query: str, limit: int) -> list[dict[str, Any]]:
    response = requests.get(
        "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts",
        params={"q": query, "limit": limit, "sort": "top"},
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    items = []
    for post in response.json().get("posts", []):
        author = post.get("author") or {}
        labels = {label.get("val") for label in (author.get("labels") or []) + (post.get("labels") or [])}
        if labels & ADULT_LABELS:
            continue
        handle = author.get("handle") or ""
        post_id = (post.get("uri") or "").rsplit("/", 1)[-1]
        text = ((post.get("record") or {}).get("text") or "").strip()
        items.append({
            "platform": "bluesky",
            "title": text.split("\n")[0][:120],
            "summary": text[:500],
            "url": f"https://bsky.app/profile/{handle}/post/{post_id}" if handle and post_id else "",
            "source": f"@{handle}" if handle else "bsky.app",
            "date": (post.get("record") or {}).get("createdAt"),
            "metrics": {"likes": post.get("likeCount"), "reposts": post.get("repostCount"), "replies": post.get("replyCount")},
        })
    return items


SOURCES: dict[str, Callable[[str, int], list[dict[str, Any]]]] = {
    "hackernews": _hackernews,
    "reddit": _reddit,
    "bluesky": _bluesky,
}


def search_community(query: str = "", source: str = "all", limit: int = 5) -> dict[str, Any]:
    """Search Hacker News, Reddit and Bluesky. One failing source does not hide the others' results."""
    try:
        query = (query or "").strip()
        limit = max(1, min(int(limit or 5), 10))
        source = (source or "all").strip().lower()
        wanted = list(SOURCES) if source not in SOURCES else [source]
        if not query:
            return {"tool": "search_community", "query": query, "sources": wanted, "items": [], "errors": {}}

        items: list[dict[str, Any]] = []
        errors: dict[str, str] = {}
        for name in wanted:
            try:
                items.extend(SOURCES[name](query, limit))
            except Exception as exc:
                errors[name] = f"{type(exc).__name__}: {exc}"
        if errors and not items:
            raise RuntimeError("All sources failed: " + "; ".join(f"{k}: {v}" for k, v in errors.items()))
        return {"tool": "search_community", "query": query, "sources": wanted, "items": items, "errors": errors}
    except Exception as exc:
        return err("search_community", exc)
