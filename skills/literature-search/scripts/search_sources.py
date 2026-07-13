#!/usr/bin/env python3
"""Search scholarly sources and normalize candidates without ranking relevance."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_SOURCES = ("openalex", "crossref", "semantic-scholar")


def load_strategy(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("input must be a JSON object")
    raw_queries = data.get("queries")
    if not isinstance(raw_queries, list) or not raw_queries:
        raise ValueError("queries must be a non-empty list")
    queries = []
    for index, item in enumerate(raw_queries, 1):
        if isinstance(item, str):
            query, label = item.strip(), f"Q{index}"
        elif isinstance(item, dict):
            query = str(item.get("query", "")).strip()
            label = str(item.get("label", f"Q{index}"))
        else:
            raise ValueError(f"query {index} must be a string or object")
        if not query:
            raise ValueError(f"query {index} is empty")
        queries.append({"label": label, "query": query})
    limit = int(data.get("limit", 10))
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")
    return {
        "research_question": data.get("research_question"),
        "queries": queries,
        "from_year": data.get("from_year"),
        "to_year": data.get("to_year"),
        "languages": data.get("languages", []),
        "include_types": data.get("include_types", []),
        "exclude": data.get("exclude", []),
        "limit": limit,
    }


def request_json(
    url: str,
    cache_dir: Path,
    timeout: float,
    retries: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        return {"status": "planned", "data": None}
    cache = cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"
    if cache.exists():
        return {"status": "cached", "data": json.loads(cache.read_text(encoding="utf-8"))}
    headers = {"User-Agent": "Boya/2.0 (+https://github.com/DylanChiang-Dev/boya)"}
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=headers), timeout=timeout
            ) as response:
                data = json.load(response)
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"status": "ok", "data": data}
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                return {"status": "error", "error": f"HTTP {exc.code}", "data": None}
            retry_after = exc.headers.get("Retry-After")
            delay = min(float(retry_after), 10.0) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt == retries:
                return {"status": "error", "error": str(exc), "data": None}
            time.sleep(2**attempt)
    return {"status": "error", "error": "unreachable", "data": None}


def normalize_title(value: str | None) -> str:
    return re.sub(r"[^\w]+", "", (value or "").casefold())


def crossref(data: Any) -> list[dict[str, Any]]:
    items = (data.get("message") or {}).get("items", []) if isinstance(data, dict) else []
    return [
        {
            "title": (item.get("title") or [None])[0],
            "authors": [
                " ".join(filter(None, (a.get("given"), a.get("family"))))
                for a in item.get("author", [])
            ],
            "year": ((item.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0],
            "venue": (item.get("container-title") or [None])[0],
            "doi": item.get("DOI"),
            "type": item.get("type"),
            "source_id": item.get("URL"),
        }
        for item in items
    ]


def openalex(data: Any) -> list[dict[str, Any]]:
    return [
        {
            "title": item.get("display_name"),
            "authors": [
                a.get("author", {}).get("display_name")
                for a in item.get("authorships", [])
            ],
            "year": item.get("publication_year"),
            "venue": ((item.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "doi": ((item.get("ids") or {}).get("doi") or "").removeprefix("https://doi.org/") or None,
            "type": item.get("type"),
            "source_id": item.get("id"),
        }
        for item in (data.get("results", []) if isinstance(data, dict) else [])
    ]


def semantic(data: Any) -> list[dict[str, Any]]:
    return [
        {
            "title": item.get("title"),
            "authors": [a.get("name") for a in item.get("authors", [])],
            "year": item.get("year"),
            "venue": item.get("venue"),
            "doi": (item.get("externalIds") or {}).get("DOI"),
            "type": None,
            "source_id": item.get("paperId"),
        }
        for item in (data.get("data", []) if isinstance(data, dict) else [])
    ]


def build_requests(strategy: dict[str, Any], sources: set[str]) -> list[dict[str, str]]:
    requests = []
    limit = strategy["limit"]
    email = os.environ.get("BOYA_CONTACT_EMAIL")
    for query in strategy["queries"]:
        label, text = query["label"], query["query"]
        if "openalex" in sources:
            filters = [f"title.search:{text}"]
            if strategy["from_year"]:
                filters.append(f"from_publication_date:{strategy['from_year']}-01-01")
            if strategy["to_year"]:
                filters.append(f"to_publication_date:{strategy['to_year']}-12-31")
            params = urllib.parse.urlencode(
                {"filter": ",".join(filters), "per-page": limit, "sort": "cited_by_count:desc"}
            )
            requests.append(
                {"label": label, "query": text, "source": "openalex", "url": f"https://api.openalex.org/works?{params}"}
            )
        if "crossref" in sources:
            params: dict[str, Any] = {"query.bibliographic": text, "rows": limit}
            filters = []
            if strategy["from_year"]:
                filters.append(f"from-pub-date:{strategy['from_year']}-01-01")
            if strategy["to_year"]:
                filters.append(f"until-pub-date:{strategy['to_year']}-12-31")
            if filters:
                params["filter"] = ",".join(filters)
            if email:
                params["mailto"] = email
            requests.append(
                {
                    "label": label,
                    "query": text,
                    "source": "crossref",
                    "url": f"https://api.crossref.org/works?{urllib.parse.urlencode(params)}",
                }
            )
        if "semantic-scholar" in sources:
            params = {
                "query": text,
                "limit": min(limit, 100),
                "fields": "title,authors,year,venue,externalIds",
            }
            if strategy["from_year"] or strategy["to_year"]:
                start = strategy["from_year"] or ""
                end = strategy["to_year"] or ""
                params["year"] = f"{start}-{end}"
            requests.append(
                {
                    "label": label,
                    "query": text,
                    "source": "semantic-scholar",
                    "url": "https://api.semanticscholar.org/graph/v1/paper/search?"
                    + urllib.parse.urlencode(params),
                }
            )
    return requests


def deduplicate(hits: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for hit in hits:
        candidate = hit["candidate"]
        key = normalize_title(candidate.get("title"))
        if not key:
            key = f"{hit['source']}:{candidate.get('source_id')}"
        if key not in merged:
            merged[key] = {
                **candidate,
                "evidence": [],
                "relevance": None,
                "include_decision": None,
            }
        merged[key]["evidence"].append(
            {
                "source": hit["source"],
                "source_id": candidate.get("source_id"),
                "query_label": hit["query_label"],
                "query": hit["query"],
            }
        )
    return list(merged.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="search strategy JSON")
    parser.add_argument("--output", type=Path, required=True, help="candidate evidence JSON")
    parser.add_argument("--cache-dir", type=Path, default=Path(".boya-cache/literature-search"))
    parser.add_argument("--sources", nargs="+", choices=DEFAULT_SOURCES, default=list(DEFAULT_SOURCES))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true", help="build requests without network access")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        strategy = load_strategy(args.input)
        requests = build_requests(strategy, set(args.sources))
        parsers = {"openalex": openalex, "crossref": crossref, "semantic-scholar": semantic}
        query_log, hits = [], []
        for request in requests:
            response = request_json(
                request["url"], args.cache_dir, args.timeout, args.retries, args.dry_run
            )
            candidates = parsers[request["source"]](response["data"]) if response["data"] else []
            query_log.append(
                {
                    **request,
                    "status": response["status"],
                    "error": response.get("error"),
                    "candidate_count": len(candidates),
                }
            )
            hits.extend(
                {
                    "source": request["source"],
                    "query_label": request["label"],
                    "query": request["query"],
                    "candidate": candidate,
                }
                for candidate in candidates
            )
        output = {
            "schema_version": "1.0",
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "notice": "Candidates are unverified. Relevance and inclusion remain undecided.",
            "strategy": strategy,
            "queries": query_log,
            "candidates": deduplicate(hits),
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
