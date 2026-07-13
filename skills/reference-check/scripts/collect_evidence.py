#!/usr/bin/env python3
"""Collect bibliographic evidence without deciding whether a reference is false."""

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

DOI_RE = re.compile(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", re.IGNORECASE)
DEFAULT_SOURCES = ("crossref", "datacite", "openalex", "semantic-scholar")


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    decoded = urllib.parse.unquote(value).strip()
    decoded = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", decoded, flags=re.I)
    decoded = re.sub(r"^doi:\s*", "", decoded, flags=re.I)
    match = DOI_RE.search(decoded)
    return match.group(0).rstrip(".,;)").lower() if match else None


def load_references(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    refs = data.get("references") if isinstance(data, dict) else data
    if not isinstance(refs, list):
        raise ValueError("input must be a JSON list or an object with a references list")
    normalized = []
    for index, item in enumerate(refs, 1):
        if not isinstance(item, dict):
            raise ValueError(f"reference {index} must be an object")
        title = str(item.get("title", "")).strip()
        doi = normalize_doi(item.get("doi"))
        if not title and not doi:
            raise ValueError(f"reference {index} needs title or doi")
        normalized.append(
            {
                "id": str(item.get("id", index)),
                "title": title,
                "authors": item.get("authors", []),
                "year": item.get("year"),
                "type": item.get("type"),
                "doi": doi,
            }
        )
    return normalized


def cache_path(cache_dir: Path, url: str) -> Path:
    return cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()}.json"


def request_json(
    url: str,
    cache_dir: Path,
    timeout: float,
    retries: int,
    dry_run: bool,
) -> dict[str, Any]:
    if dry_run:
        return {"status": "planned", "url": url, "data": None}
    cached = cache_path(cache_dir, url)
    if cached.exists():
        return {"status": "cached", "url": url, "data": json.loads(cached.read_text(encoding="utf-8"))}
    headers = {"User-Agent": "Boya/2.0 (+https://github.com/DylanChiang-Dev/boya)"}
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = json.load(response)
            cache_dir.mkdir(parents=True, exist_ok=True)
            cached.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            return {"status": "ok", "url": url, "data": data}
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retries:
                return {"status": "error", "url": url, "error": f"HTTP {exc.code}"}
            retry_after = exc.headers.get("Retry-After")
            delay = min(float(retry_after), 10.0) if retry_after and retry_after.isdigit() else 2**attempt
            time.sleep(delay)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            if attempt == retries:
                return {"status": "error", "url": url, "error": str(exc)}
            time.sleep(2**attempt)
    return {"status": "error", "url": url, "error": "unreachable"}


def crossref_candidates(data: Any) -> list[dict[str, Any]]:
    message = data.get("message", {}) if isinstance(data, dict) else {}
    items = message.get("items", [message]) if isinstance(message, dict) else []
    return [
        {
            "title": (item.get("title") or [None])[0],
            "authors": [
                " ".join(filter(None, (a.get("given"), a.get("family"))))
                for a in item.get("author", [])
            ],
            "year": ((item.get("issued", {}).get("date-parts") or [[None]])[0] or [None])[0],
            "venue": (item.get("container-title") or [None])[0],
            "doi": normalize_doi(item.get("DOI")),
            "type": item.get("type"),
        }
        for item in items[:3]
    ]


def datacite_candidates(data: Any) -> list[dict[str, Any]]:
    records = data.get("data", []) if isinstance(data, dict) else []
    if isinstance(records, dict):
        records = [records]
    result = []
    for record in records[:3]:
        attrs = record.get("attributes", {})
        titles = attrs.get("titles") or []
        result.append(
            {
                "title": titles[0].get("title") if titles else None,
                "authors": [c.get("name") for c in attrs.get("creators", [])],
                "year": attrs.get("publicationYear"),
                "venue": attrs.get("publisher"),
                "doi": normalize_doi(attrs.get("doi") or record.get("id")),
                "type": (attrs.get("types") or {}).get("resourceTypeGeneral"),
            }
        )
    return result


def openalex_candidates(data: Any) -> list[dict[str, Any]]:
    return [
        {
            "title": item.get("display_name"),
            "authors": [
                a.get("author", {}).get("display_name")
                for a in item.get("authorships", [])
            ],
            "year": item.get("publication_year"),
            "venue": ((item.get("primary_location") or {}).get("source") or {}).get("display_name"),
            "doi": normalize_doi((item.get("ids") or {}).get("doi")),
            "type": item.get("type"),
            "openalex_id": item.get("id"),
        }
        for item in (data.get("results", []) if isinstance(data, dict) else [])[:3]
    ]


def semantic_candidates(data: Any) -> list[dict[str, Any]]:
    return [
        {
            "title": item.get("title"),
            "authors": [a.get("name") for a in item.get("authors", [])],
            "year": item.get("year"),
            "venue": item.get("venue"),
            "doi": normalize_doi((item.get("externalIds") or {}).get("DOI")),
            "type": None,
            "semantic_scholar_id": item.get("paperId"),
        }
        for item in (data.get("data", []) if isinstance(data, dict) else [])[:3]
    ]


def add_query(
    queries: list[dict[str, Any]],
    source: str,
    url: str,
    parser,
    args: argparse.Namespace,
) -> None:
    response = request_json(url, args.cache_dir, args.timeout, args.retries, args.dry_run)
    candidates = parser(response.get("data")) if response.get("data") is not None else []
    queries.append(
        {
            "source": source,
            "status": response["status"],
            "request_url": url,
            "error": response.get("error"),
            "candidates": candidates,
        }
    )


def collect(reference: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    queries: list[dict[str, Any]] = []
    sources = set(args.sources)
    email = os.environ.get("BOYA_CONTACT_EMAIL")
    mailto = f"&mailto={urllib.parse.quote(email)}" if email else ""
    doi = reference["doi"]
    if doi and "crossref" in sources:
        url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"
        if email:
            url += f"?mailto={urllib.parse.quote(email)}"
        add_query(queries, "crossref", url, crossref_candidates, args)
    if doi and "datacite" in sources:
        url = f"https://api.datacite.org/dois/{urllib.parse.quote(doi, safe='')}"
        add_query(queries, "datacite", url, datacite_candidates, args)
    title = reference["title"]
    if title and "crossref" in sources:
        params = urllib.parse.urlencode({"query.bibliographic": title, "rows": 3})
        add_query(queries, "crossref", f"https://api.crossref.org/works?{params}{mailto}", crossref_candidates, args)
    if title and "openalex" in sources:
        params = urllib.parse.urlencode({"filter": f"title.search:{title}", "per-page": 3})
        add_query(queries, "openalex", f"https://api.openalex.org/works?{params}", openalex_candidates, args)
    if title and "semantic-scholar" in sources:
        params = urllib.parse.urlencode(
            {"query": title, "limit": 3, "fields": "title,authors,year,venue,externalIds"}
        )
        add_query(
            queries,
            "semantic-scholar",
            f"https://api.semanticscholar.org/graph/v1/paper/search?{params}",
            semantic_candidates,
            args,
        )
    return {"reference": reference, "queries": queries, "decision": None}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="normalized reference JSON")
    parser.add_argument("--output", type=Path, required=True, help="evidence JSON")
    parser.add_argument("--cache-dir", type=Path, default=Path(".boya-cache/reference-check"))
    parser.add_argument("--sources", nargs="+", choices=DEFAULT_SOURCES, default=list(DEFAULT_SOURCES))
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--dry-run", action="store_true", help="build requests without network access")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        references = load_references(args.input)
        evidence = {
            "schema_version": "1.0",
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "notice": "Evidence only. A missing result is not a fabrication finding.",
            "records": [collect(reference, args) for reference in references],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
