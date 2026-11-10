from __future__ import annotations

from typing import Any

from tools._shared import domain


def _src(item: dict[str, Any]) -> str:
    src = item.get("source") or domain(item.get("url", ""))
    url = item.get("url") or ""
    return f"[{src}]({url})" if url else (src or "")


def _bullet(item: dict[str, Any]) -> str:
    text = (item.get("summary") or item.get("title") or "").strip().replace("\n", " ")
    if len(text) > 280:
        text = text[:277] + "..."
    return f"- {text} - {_src(item)}"


DIGEST_MAX_ITEMS = 10  # keeps the digest a ~5 minute read
WORDS_PER_MINUTE = 200


def _digest_5min(items: list[dict[str, Any]], headline: str, searched_with: list[str]) -> str:
    """Numbered quick-read digest: one short entry per item with its link, then all sources and the searches used."""
    items = items[:DIGEST_MAX_ITEMS]
    entries = []
    for index, item in enumerate(items, start=1):
        title = (item.get("title") or "").strip() or (item.get("summary") or "").strip()[:80]
        summary = (item.get("summary") or "").strip().replace("\n", " ")
        if len(summary) > 300:
            summary = summary[:297] + "..."
        link = _src(item) or "(không có link)"
        line = f"{index}. **{title}**" + (f" — {summary}" if summary and summary != title else "")
        entries.append(f"{line}\n   🔗 {link}")

    sources: dict[str, str] = {}
    for item in items:
        url = item.get("url") or ""
        if url and url not in sources:
            sources[url] = f"- [{item.get('source') or domain(url)}]({url}) — {(item.get('title') or '').strip()}"

    body = "\n\n".join(entries)
    minutes = max(1, round(len(body.split()) / WORDS_PER_MINUTE))
    parts = [
        f"# {headline or 'Bản tin 5 phút'}",
        f"_⏱ ~{minutes} phút đọc · {len(items)} tin · {len(sources)} nguồn_",
        "",
        body or "_Chưa có tin nào._",
        "",
        "---",
        "**📚 Nguồn & tài liệu tham khảo**",
        *(sources.values() or ["- (không có link)"]),
    ]
    if searched_with:
        parts += ["", "**🔎 Agent đã tìm bằng**", *[f"- {step}" for step in searched_with]]
    return "\n".join(parts)


def render_digest(
    items: list[dict[str, Any]] | None = None,
    template: str = "sections",
    headline: str = "",
    searched_with: list[str] | None = None,
) -> dict[str, Any]:
    items = items or []
    if template == "digest_5min":
        items = items[:DIGEST_MAX_ITEMS]
        markdown = _digest_5min(items, headline, [str(step) for step in (searched_with or [])])
    elif template == "brief":
        markdown = (f"**{headline}**\n\n" if headline else "") + "\n".join(_bullet(item) for item in items[:5])
    elif template == "bullets":
        markdown = "\n".join(_bullet(item) for item in items)
    elif template == "thread":
        markdown = "\n\n".join(f"{index + 1}/ {_bullet(item)[2:]}" for index, item in enumerate(items))
    elif template == "daily_ai_vn":
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            groups.setdefault(item.get("section", "Tin chính"), []).append(item)
        parts = [f"**{headline or 'Tin tức hôm nay'}**", ""]
        for section, section_items in groups.items():
            parts += [f"**{section}**", *[_bullet(item) for item in section_items], ""]
        markdown = "\n".join(parts)
    else:
        groups: dict[str, list[dict[str, Any]]] = {}
        for item in items:
            groups.setdefault(item.get("section", "Tổng hợp"), []).append(item)
        parts = ([f"# {headline}", ""] if headline else [])
        for section, section_items in groups.items():
            parts += [f"## {section}", *[_bullet(item) for item in section_items], ""]
        markdown = "\n".join(parts)
    return {"tool": "render_digest", "template": template, "markdown": markdown, "item_count": len(items)}

