"""Tool Unit Test.

Rules:
- Offline only: mock HTTP with `fake_http`, set fake keys with `monkeypatch.setenv`.
- One behaviour per test. Name the test after the behaviour, not the function.
- Done = `pytest tests/ -v` shows 0 skipped, 0 failed.
"""
from __future__ import annotations

import requests

from conftest import FakeResponse  # noqa: F401  (you will need it)
from tools.clarify.tool import ask_user
from tools import TOOL_FUNCTIONS  # noqa: F401

format_tool = TOOL_FUNCTIONS["format"]
lookup_tool = TOOL_FUNCTIONS["lookup"]
send_tool = TOOL_FUNCTIONS["send"]
clarify_tool = TOOL_FUNCTIONS["clarify"]
social_search_tool = TOOL_FUNCTIONS["social_search"]
timeline_tool = TOOL_FUNCTIONS["timeline"]
fetch_tool = TOOL_FUNCTIONS["fetch"]

TODO = "TODO(student): implement this test"


# ---------------- clarify ----------------

def test_clarify_choice_returns_options_and_awaits_user() -> None:
    # Call clarify with response_type="choice" and 2 options.
    # Assert: options are returned unchanged, awaiting_user is True.
    #pytest.skip(TODO)
    options = ["Option A", "Option B"]
    result = clarify_tool(question="Choose one:", response_type="choice", options=options)
    
    # Assert: options are returned unchanged, awaiting_user is True.
    assert result["options"] == options
    assert result["awaiting_user"] is True
    assert result["response_type"] == "choice"

# ---------------- format ----------------

def test_format_sections_groups_items_by_section() -> None:
    items = [
        {"title": "a1", "url": "https://a.com/1", "section": "A"},
        {"title": "b1", "url": "https://b.com/1", "section": "B"},
        {"title": "a2", "url": "https://a.com/2", "section": "A"},
    ]

    markdown = TOOL_FUNCTIONS["format"](items, template="sections")["markdown"]

    assert markdown.count("## A") == 1
    assert markdown.count("## B") == 1


def test_format_thread_numbers_items() -> None:
    items = [{"title": "first", "url": "https://x.com/1"}, {"title": "second", "url": "https://x.com/2"}]

    markdown = TOOL_FUNCTIONS["format"](items, template="thread")["markdown"]

    posts = markdown.split("\n\n")
    assert posts[0].startswith("1/ first")
    assert posts[1].startswith("2/ second")


def test_format_empty_items_does_not_crash() -> None:
    for items in (None, []):
        result = TOOL_FUNCTIONS["format"](items, template="sections")
        assert result["item_count"] == 0


# ---------------- send (guardrail) ----------------

def test_send_confirmed_posts_to_telegram(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "42")
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"]("digest", confirmed=True)

    assert len(calls) == 1
    assert calls[0]["method"] == "POST"
    assert "test-token" in calls[0]["url"]
    assert calls[0]["json"]["chat_id"] == "42"
    assert calls[0]["json"]["text"] == "digest"
    assert result["status"] == "sent"


def test_send_confirmed_without_env_returns_error_and_no_request(fake_http) -> None:
    calls = fake_http(FakeResponse({"ok": True}))

    result = TOOL_FUNCTIONS["send"]("digest", confirmed=True)

    assert result["error"] == "RuntimeError"
    assert calls == []


# ---------------- lookup ----------------

def test_lookup_without_timeframe_omits_time_range(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")
    calls = fake_http(FakeResponse({"results": []}))

    TOOL_FUNCTIONS["lookup"]("AI", timeframe=None)

    assert "time_range" not in calls[0]["json"]


# ---------------- fetch ----------------

def test_fetch_maps_firecrawl_response(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {
        "markdown": "Body text",
        "metadata": {"title": "T", "sourceURL": "https://www.example.org/post"},
    }}))

    item = TOOL_FUNCTIONS["fetch"]("https://www.example.org/post")["items"][0]

    assert item["title"] == "T"
    assert item["url"] == "https://www.example.org/post"
    assert item["source"] == "example.org"
    assert item["summary"] == "Body text"


def test_fetch_truncates_markdown_to_4000_chars(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("FIRECRAWL_API_KEY", "test-key")
    fake_http(FakeResponse({"data": {"markdown": "x" * 5000, "metadata": {}}}))

    item = TOOL_FUNCTIONS["fetch"]("https://example.org")["items"][0]

    assert len(item["summary"]) == 4000


# ---------------- timeline / social_search ----------------

def test_timeline_respects_limit_and_skips_items_without_id(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    raw = [_tweet(None, "no id")] + [_tweet(str(i)) for i in range(1, 7)]
    fake_http(FakeResponse({"timeline": raw}))

    items = TOOL_FUNCTIONS["timeline"]("sama", limit=3)["items"]

    assert len(items) == 3
    assert [item["url"] for item in items] == [f"https://x.com/sama/status/{i}" for i in (1, 2, 3)]


def test_social_search_passes_search_type(monkeypatch, fake_http) -> None:
    monkeypatch.setenv("RAPIDAPI_KEY", "test-key")
    calls = fake_http(FakeResponse({"timeline": []}))

    TOOL_FUNCTIONS["social_search"]("OpenAI", search_type="Top")

    assert calls[0]["params"] == {"query": "OpenAI", "search_type": "Top"}


# ---------------- policy (local knowledge + trust boundary) ----------------

def test_policy_empty_query_returns_no_results() -> None:
    assert TOOL_FUNCTIONS["policy"]("")["results"] == []


def test_policy_area_filter_only_returns_that_area() -> None:
    results = TOOL_FUNCTIONS["policy"]("data privacy personal information", policy_area="data_privacy")["results"]

    assert results
    assert all(r["policy_area"] == "data_privacy" for r in results)


def test_policy_instruction_like_lines_go_to_untrusted_text() -> None:
    results = TOOL_FUNCTIONS["policy"]("injection probe citation", policy_area="source_citation", top_k=10)["results"]

    probe = next(r for r in results if r["section"] == "Injection probe")
    assert any("viral tweet" in line for line in probe["untrusted_text"])
    assert "viral tweet" not in probe["facts"]


# ---------------- papers (the tool our team changed: stopword fix) ----------------
# The team added no new tool, so these 3 tests cover `papers`, which we modified.

ATOM_ONE_ENTRY = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>1</opensearch:totalResults>
  <entry>
    <id>http://arxiv.org/abs/2201.11903v6</id>
    <title>Chain-of-Thought Prompting
 Elicits Reasoning</title>
    <summary>We explore how
 chain of thought helps.</summary>
    <author><name>Jason Wei</name></author>
    <published>2022-01-28T00:00:00Z</published>
    <updated>2023-01-10T00:00:00Z</updated>
    <link title="pdf" href="http://arxiv.org/pdf/2201.11903v6" rel="related"/>
    <arxiv:primary_category term="cs.CL"/>
    <category term="cs.CL"/>
  </entry>
</feed>"""


def _no_rate_limit(monkeypatch) -> None:
    import tools.papers.tool as papers

    monkeypatch.setattr(papers, "_rate_limit_arxiv", lambda: None)


def test_papers_happy_path_maps_atom_entry_and_drops_stopwords(monkeypatch, fake_http) -> None:
    _no_rate_limit(monkeypatch)
    calls = fake_http(FakeResponse(text=ATOM_ONE_ENTRY))

    result = TOOL_FUNCTIONS["papers"]("chain of thought", max_results=1)

    assert calls[0]["params"]["search_query"] == "all:chain AND all:thought"
    assert result["total_results"] == 1
    item = result["items"][0]
    assert item["title"] == "Chain-of-Thought Prompting  Elicits Reasoning"
    assert item["summary"] == "We explore how chain of thought helps."
    assert item["authors"] == ["Jason Wei"]
    assert item["pdf_url"] == "http://arxiv.org/pdf/2201.11903v6"


def test_papers_bad_input_from_model_is_clamped(monkeypatch, fake_http) -> None:
    _no_rate_limit(monkeypatch)
    calls = fake_http(FakeResponse(text=ATOM_ONE_ENTRY))

    TOOL_FUNCTIONS["papers"]("chain of thought", max_results=999, sort_by="newest")

    assert calls[0]["params"]["max_results"] == 10
    assert calls[0]["params"]["sortBy"] == "relevance"


def test_papers_http_error_returns_error_dict(monkeypatch, fake_http) -> None:
    _no_rate_limit(monkeypatch)
    fake_http(requests.ConnectionError("arXiv unreachable"))

    result = TOOL_FUNCTIONS["papers"]("chain of thought")

    assert result["error"] == "ConnectionError"
    assert "arXiv unreachable" in result["message"]


# ---------------- community (new tool: Hacker News + Reddit + Bluesky) ----------------

HN_JSON = {"hits": [{"objectID": "1", "title": "GPT-5 is out", "url": "https://openai.com/gpt-5", "points": 10, "num_comments": 3}]}
REDDIT_ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>GPT-5 first impressions</title>
    <link href="https://www.reddit.com/r/OpenAI/comments/abc/gpt5/"/>
    <category term="OpenAI" label="r/OpenAI"/>
    <content type="html">&lt;p&gt;Pretty &lt;b&gt;good&lt;/b&gt;&lt;/p&gt;</content>
    <updated>2026-11-01T00:00:00+00:00</updated>
  </entry>
</feed>"""
BSKY_JSON = {"posts": [
    {"uri": "at://did:plc:a/app.bsky.feed.post/xyz", "author": {"handle": "alice.bsky.social"},
     "record": {"text": "GPT-5 thoughts", "createdAt": "2026-11-02T00:00:00Z"}, "likeCount": 5},
    {"uri": "at://did:plc:b/app.bsky.feed.post/nsfw", "author": {"handle": "spam.bsky.social", "labels": [{"val": "porn"}]},
     "record": {"text": "GPT-5 spam"}},
]}


def _fake_community_http(monkeypatch, fail: set[str] | None = None) -> list[str]:
    """Route each source URL to its own fake payload; sources in `fail` return HTTP 429."""
    fail = fail or set()
    calls: list[str] = []
    payloads = {
        "hn.algolia.com": ("hackernews", FakeResponse(HN_JSON)),
        "reddit.com": ("reddit", FakeResponse(text=REDDIT_ATOM)),
        "bsky.app": ("bluesky", FakeResponse(BSKY_JSON)),
    }

    def _get(url: str, **kwargs):
        calls.append(url)
        for host, (name, response) in payloads.items():
            if host in url:
                return FakeResponse(status_code=429) if name in fail else response
        raise AssertionError(f"unexpected URL {url}")

    monkeypatch.setattr(requests, "get", _get)
    return calls


def test_community_happy_path_merges_all_sources_and_skips_adult_posts(monkeypatch) -> None:
    _fake_community_http(monkeypatch)

    result = TOOL_FUNCTIONS["community"]("GPT-5")

    by_platform = {item["platform"]: item for item in result["items"]}
    assert set(by_platform) == {"hackernews", "reddit", "bluesky"}
    assert by_platform["hackernews"]["url"] == "https://news.ycombinator.com/item?id=1"
    assert by_platform["reddit"]["source"] == "r/OpenAI"
    assert by_platform["reddit"]["summary"] == "Pretty good"
    assert by_platform["bluesky"]["url"] == "https://bsky.app/profile/alice.bsky.social/post/xyz"
    assert len([i for i in result["items"] if i["platform"] == "bluesky"]) == 1
    assert result["errors"] == {}


def test_community_bad_input_from_model(monkeypatch) -> None:
    calls = _fake_community_http(monkeypatch)

    assert TOOL_FUNCTIONS["community"]("   ")["items"] == []
    assert calls == []

    result = TOOL_FUNCTIONS["community"]("GPT-5", source="twitter", limit=999)
    assert result["sources"] == ["hackernews", "reddit", "bluesky"]

    TOOL_FUNCTIONS["community"]("GPT-5", source="Reddit")
    assert "reddit.com" in calls[-1]


def test_community_one_failing_source_keeps_the_others(monkeypatch) -> None:
    _fake_community_http(monkeypatch, fail={"reddit"})

    result = TOOL_FUNCTIONS["community"]("GPT-5")

    assert {item["platform"] for item in result["items"]} == {"hackernews", "bluesky"}
    assert "HTTPError" in result["errors"]["reddit"]


def test_community_all_sources_failing_returns_error_dict(monkeypatch) -> None:
    _fake_community_http(monkeypatch, fail={"hackernews", "reddit", "bluesky"})

    result = TOOL_FUNCTIONS["community"]("GPT-5")

    assert result["error"] == "RuntimeError"
    assert "All sources failed" in result["message"]


# ---------------- format: digest_5min (5-minute newsletter) ----------------

def test_digest_5min_numbers_items_with_links_and_lists_sources_and_searches() -> None:
    items = [
        {"title": "GPT-6 ra mắt", "url": "https://www.theverge.com/a", "source": "theverge.com", "summary": "OpenAI công bố GPT-6."},
        {"title": "Spain wins", "url": "https://bbc.com/b", "summary": "Spain beat Argentina 1-0."},
        {"title": "Duplicate link", "url": "https://bbc.com/b"},
    ]

    markdown = TOOL_FUNCTIONS["format"](
        items, template="digest_5min", headline="Bản tin AI", searched_with=["lookup: AI (news, day)"]
    )["markdown"]

    assert markdown.startswith("# Bản tin AI")
    assert "1. **GPT-6 ra mắt** — OpenAI công bố GPT-6.\n   🔗 [theverge.com](https://www.theverge.com/a)" in markdown
    assert "2. **Spain wins**" in markdown and "3. **Duplicate link**" in markdown
    sources = markdown.split("Nguồn & tài liệu tham khảo")[1].split("Agent đã tìm bằng")[0]
    assert sources.count("https://bbc.com/b") == 1  # each source listed once
    assert "- lookup: AI (news, day)" in markdown


def test_digest_5min_caps_items_and_handles_empty_input() -> None:
    many = [{"title": f"t{i}", "url": f"https://x.com/{i}"} for i in range(15)]

    result = TOOL_FUNCTIONS["format"](many, template="digest_5min")

    assert "10. **t9**" in result["markdown"] and "11. " not in result["markdown"]
    empty = TOOL_FUNCTIONS["format"](None, template="digest_5min")["markdown"]
    assert "Chưa có tin nào" in empty and "Agent đã tìm bằng" not in empty
