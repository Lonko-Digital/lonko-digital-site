#!/usr/bin/env python3
"""Full Option A vs B Chronicles search relevance + performance benchmark.

Eight-category suite from the Implementation Brief Part 2. Reports for each:
expected article found, rank, useful recall (top-3 / top-5), false-positive/noise
notes, and query latency. Writes JSON + human report under docs/.

Usage (from lonko-digital-site/):
  python scripts/benchmark_chronicles_search.py
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "chronicles" / "assets"
OUT_JSON = ROOT / "docs" / "_chronicles_search_bench_full.json"
OUT_TXT = ROOT / "docs" / "_chronicles_search_bench.txt"

# Fixed suite — every category has an explicit expected slug / quality intent.
# Typo query deliberately does NOT expand to the corrected spelling: that is the
# fuzzy capability under test. Neither A nor B currently implements edit-distance.
QUERY_SUITE: list[dict] = [
    {
        "id": "exact_headline",
        "label": "Exact headline phrase",
        "query": "When stable traffic hides a conversion problem",
        "expected_slug": "when-stable-traffic-hides-a-conversion-problem",
        "intent": "Exact editorial title should rank #1 with high score separation.",
    },
    {
        "id": "topic",
        "label": "Topic query",
        "query": "SEO",
        "expected_slug": "a-practical-checklist-for-seo-changes-that-might-hurt-leads",
        "expected_topic": "SEO",
        "intent": "SEO-topic articles dominate; primary How-To checklist near top.",
    },
    {
        "id": "partial",
        "label": "Partial query",
        "query": "market",
        "expected_slug": "how-to-read-a-marketing-report-without-getting-lost",
        "intent": "Partial stem should still surface marketing-report guide usefully.",
    },
    {
        "id": "typo",
        "label": "Typo / fuzzy query",
        "query": "inteligence",
        "expected_slug": "ai-answers-are-not-the-same-as-business-evidence",
        "intent": "Misspelling of 'intelligence' — requires fuzzy; expect miss without it.",
        "fuzzy": True,
    },
    {
        "id": "owner_nl",
        "label": "Natural-language business-owner query",
        "query": "why aren't my ads converting",
        "expected_slug": "when-stable-traffic-hides-a-conversion-problem",
        "intent": "Owner-language about conversions should surface the conversion analysis.",
        "acceptable_slugs": [
            "when-stable-traffic-hides-a-conversion-problem",
            "google-ads-budget-pacing-for-busy-owners",
            "the-hidden-cost-of-unverified-tracking",
        ],
    },
    {
        "id": "body_only",
        "label": "Answer lives mainly in body text",
        "query": "xylophone funnel audit",
        "expected_slug": "systems-habits-worth-keeping-as-you-scale",
        "intent": "Phrase exists only in body — metadata-only index must miss.",
    },
    {
        "id": "entity",
        "label": "Common platform / entity query",
        "query": "Google Ads",
        "expected_slug": "google-ads-budget-pacing-for-busy-owners",
        "intent": "Entity/platform name should rank the dedicated Google Ads piece highly.",
        "acceptable_slugs": [
            "google-ads-budget-pacing-for-busy-owners",
            "when-stable-traffic-hides-a-conversion-problem",
            "a-calmer-way-to-review-weekly-ad-performance",
        ],
    },
    {
        "id": "ambiguous",
        "label": "Deliberately ambiguous query",
        "query": "growth",
        "expected_slug": "spend-less-guesswork",
        "expected_topic": "Growth",
        "intent": "Ambiguous single token — Growth-topic pieces OK; watch for flood/noise.",
        "acceptable_slugs": [
            "spend-less-guesswork",
            "what-a-local-shop-needs-from-marketing-data",
            "how-to-read-a-marketing-report-without-getting-lost",
            "measuring-landing-page-friction-without-vanity-charts",
            "why-dashboard-green-is-not-a-strategy",
            "attribution-confidence-in-plain-language",
        ],
    },
]


def tokenize(q: str) -> list[str]:
    return [t for t in re.split(r"[^a-z0-9]+", q.lower().strip()) if t]


def score_a(entry: dict, tokens: list[str]) -> float:
    title = (entry.get("title") or "").lower()
    deck = (entry.get("deck") or "").lower()
    topic = (entry.get("topic") or "").lower()
    tags = " ".join(entry.get("tags") or []).lower()
    ctype = (entry.get("content_type") or "").lower()
    score = 0.0
    for tok in tokens:
        if title == tok:
            score += 50
        if tok in title:
            score += 20
        if tok in topic:
            score += 12
        if tok in tags:
            score += 10
        if tok in deck:
            score += 8
        if tok in ctype:
            score += 4
    # Phrase bonus for multi-token exact title containment
    if len(tokens) >= 3:
        phrase = " ".join(tokens)
        if phrase in title:
            score += 80
    return score


def score_b(entry: dict, tokens: list[str]) -> float:
    score = score_a(entry, tokens)
    body = (entry.get("body") or entry.get("excerpt") or "").lower()
    for tok in tokens:
        if tok in body:
            score += 2
    if len(tokens) >= 3:
        phrase = " ".join(tokens)
        if phrase in body:
            score += 40
    return score


def rank_index(index: list[dict], scorer, query: str) -> list[tuple[float, dict]]:
    tokens = tokenize(query)
    ranked: list[tuple[float, dict]] = []
    for entry in index:
        s = scorer(entry, tokens)
        if s > 0:
            ranked.append((s, entry))
    ranked.sort(key=lambda x: (-x[0], x[1].get("slug") or ""))
    return ranked


def analyze(
    ranked: list[tuple[float, dict]],
    item: dict,
    *,
    elapsed_ms: float,
) -> dict:
    expected = item.get("expected_slug")
    acceptable = set(item.get("acceptable_slugs") or [])
    if expected:
        acceptable.add(expected)

    top5 = [
        {
            "rank": i + 1,
            "slug": e.get("slug"),
            "title": e.get("title"),
            "topic": e.get("topic"),
            "score": s,
        }
        for i, (s, e) in enumerate(ranked[:5])
    ]
    top3_slugs = [x["slug"] for x in top5[:3]]
    top5_slugs = [x["slug"] for x in top5]

    expected_rank = None
    for i, (s, e) in enumerate(ranked):
        if e.get("slug") == expected:
            expected_rank = i + 1
            break

    # Useful recall: expected in top-3 (primary) / top-5 (secondary)
    in_top3 = expected in top3_slugs if expected else False
    in_top5 = expected in top5_slugs if expected else False
    # Acceptable-set recall for NL/entity/ambiguous where multiple answers are OK
    acceptable_in_top3 = any(s in acceptable for s in top3_slugs)
    acceptable_in_top5 = any(s in acceptable for s in top5_slugs)

    # Noise: results outside expected topic (when topic constraint exists)
    # or scores that are incidental single-token hits flooding the list
    noise_notes: list[str] = []
    expected_topic = item.get("expected_topic")
    if expected_topic and ranked:
        off_topic = [
            e.get("slug")
            for _, e in ranked[:10]
            if (e.get("topic") or "") != expected_topic
        ]
        if off_topic:
            noise_notes.append(
                f"Off-topic in top-10 ({expected_topic} expected): {', '.join(off_topic[:5])}"
                + ("…" if len(off_topic) > 5 else "")
            )

    if ranked and len(ranked) >= 8 and item["id"] in {"partial", "ambiguous", "exact_headline"}:
        # Large result sets on short/ambiguous queries = noise risk
        top_score = ranked[0][0]
        weak = sum(1 for s, _ in ranked if s < top_score * 0.25)
        if weak >= 5:
            noise_notes.append(
                f"Long tail noise: {weak}/{len(ranked)} hits score <25% of top ({top_score})"
            )
        if len(ranked) > 12:
            noise_notes.append(f"High recall flood: {len(ranked)} total hits")

    if item.get("fuzzy") and expected_rank is None:
        noise_notes.append("No fuzzy/edit-distance matching — typo returns empty (expected gap).")

    if item["id"] == "body_only" and expected_rank is None:
        noise_notes.append("Body phrase absent from metadata index (expected for Option A).")

    # Score separation for exact headline quality
    score_gap = None
    if len(ranked) >= 2:
        score_gap = round(ranked[0][0] - ranked[1][0], 1)

    return {
        "id": item["id"],
        "label": item["label"],
        "query": item["query"],
        "intent": item.get("intent"),
        "expected_slug": expected,
        "time_ms": round(elapsed_ms, 3),
        "hits": len(ranked),
        "top5": top5,
        "expected_found": expected_rank is not None,
        "expected_rank": expected_rank,
        "useful_recall_top3": in_top3,
        "useful_recall_top5": in_top5,
        "acceptable_in_top3": acceptable_in_top3,
        "acceptable_in_top5": acceptable_in_top5,
        "score_gap_1_to_2": score_gap,
        "noise_notes": noise_notes,
        "pass_primary": bool(
            in_top3
            if item["id"] not in {"owner_nl", "entity", "ambiguous", "typo"}
            else (acceptable_in_top3 if item["id"] != "typo" else False)
        ),
    }


def run_suite(index: list[dict], scorer, suite: list[dict]) -> list[dict]:
    out = []
    for item in suite:
        t0 = time.perf_counter()
        ranked = rank_index(index, scorer, item["query"])
        elapsed = (time.perf_counter() - t0) * 1000
        out.append(analyze(ranked, item, elapsed_ms=elapsed))
    return out


def verdict(results_a: list[dict], results_b: list[dict], size_a: int, size_b: int) -> dict:
    def score_card(results: list[dict]) -> dict:
        primary = sum(1 for r in results if r["pass_primary"])
        body = next(r for r in results if r["id"] == "body_only")
        typo = next(r for r in results if r["id"] == "typo")
        return {
            "primary_passes": primary,
            "primary_total": len(results),
            "body_only_found": body["expected_found"],
            "body_only_rank": body["expected_rank"],
            "typo_found": typo["expected_found"],
            "avg_ms": round(sum(r["time_ms"] for r in results) / len(results), 3),
            "max_ms": max(r["time_ms"] for r in results),
        }

    card_a = score_card(results_a)
    card_b = score_card(results_b)

    # Decision rule from brief: B if materially better discovery while inside budget
    material_quality = (
        card_b["body_only_found"] and not card_a["body_only_found"]
    ) or (card_b["primary_passes"] > card_a["primary_passes"])
    inside_budget = size_b < 200_000  # deferred on-demand index; well under page budgets

    choice = "B" if material_quality and inside_budget else ("A" if not material_quality else "B_with_caveat")
    reasoning = []
    if card_b["body_only_found"] and not card_a["body_only_found"]:
        reasoning.append(
            "B uniquely recovers the body-only phrase query (A returns 0) — material discovery gain."
        )
    if card_b["primary_passes"] >= card_a["primary_passes"]:
        reasoning.append(
            f"Primary pass count A={card_a['primary_passes']}/{card_a['primary_total']} "
            f"vs B={card_b['primary_passes']}/{card_b['primary_total']}."
        )
    if not card_a["typo_found"] and not card_b["typo_found"]:
        reasoning.append(
            "Neither option implements fuzzy matching; typo query fails equally (not decisive)."
        )
    reasoning.append(
        f"Index cost A={size_a}B vs B={size_b}B "
        f"({size_b / max(size_a, 1):.2f}x); B remains deferred/on-demand."
    )
    if choice == "B":
        reasoning.append("Decision: ship Option B.")
    return {"choice": choice, "reasoning": reasoning, "card_a": card_a, "card_b": card_b}


def format_report(
    suite: list[dict],
    results_a: list[dict],
    results_b: list[dict],
    size_a: int,
    size_b: int,
    n_docs: int,
    decision: dict,
) -> str:
    lines: list[str] = []
    lines.append("=== Chronicles search benchmark — FULL 8-category suite ===")
    lines.append(f"Corpus: {n_docs} docs")
    lines.append(
        f"Index bytes: A={size_a}  B={size_b}  (B/A={size_b / max(size_a, 1):.2f}x)"
    )
    lines.append("")
    lines.append(
        f"{'Category':<38} {'A rank':>7} {'B rank':>7} {'A top3':>7} {'B top3':>7} "
        f"{'A hits':>7} {'B hits':>7}"
    )
    lines.append("-" * 100)
    for a, b in zip(results_a, results_b):
        ar = str(a["expected_rank"] or "—")
        br = str(b["expected_rank"] or "—")
        lines.append(
            f"{a['label']:<38} {ar:>7} {br:>7} "
            f"{'Y' if a['useful_recall_top3'] else 'N':>7} "
            f"{'Y' if b['useful_recall_top3'] else 'N':>7} "
            f"{a['hits']:>7} {b['hits']:>7}"
        )

    lines.append("")
    lines.append("=== Per-query relevance detail ===")
    for a, b, item in zip(results_a, results_b, suite):
        lines.append("")
        lines.append(f"## {item['label']}")
        lines.append(f"Query: {item['query']!r}")
        lines.append(f"Expected: {item.get('expected_slug')}")
        lines.append(f"Intent: {item.get('intent')}")
        for label, r in (("Option A", a), ("Option B", b)):
            lines.append(
                f"  {label}: found={r['expected_found']} rank={r['expected_rank']} "
                f"hits={r['hits']} top3={r['useful_recall_top3']} top5={r['useful_recall_top5']} "
                f"acceptable@3={r['acceptable_in_top3']} gap1-2={r['score_gap_1_to_2']} "
                f"ms={r['time_ms']}"
            )
            tops = ", ".join(
                f"#{t['rank']} {t['slug']} ({t['score']})" for t in r["top5"]
            ) or "(none)"
            lines.append(f"    top5: {tops}")
            for note in r["noise_notes"]:
                lines.append(f"    noise: {note}")

    lines.append("")
    lines.append("=== Decision ===")
    lines.append(f"Choice: Option {decision['choice']}")
    for r in decision["reasoning"]:
        lines.append(f"- {r}")
    lines.append(
        f"Scorecard A: {decision['card_a']} | Scorecard B: {decision['card_b']}"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    path_a = ASSETS / "search-index-a.json"
    path_b = ASSETS / "search-index-b.json"
    if not path_a.is_file() or not path_b.is_file():
        print(
            "Missing search indexes. Run `python scripts/build_chronicles.py` first.",
            file=sys.stderr,
        )
        return 1

    raw_a = path_a.read_bytes()
    raw_b = path_b.read_bytes()
    index_a = json.loads(raw_a.decode("utf-8"))
    index_b = json.loads(raw_b.decode("utf-8"))

    # Ensure expected fixtures exist
    slugs = {e.get("slug") for e in index_b}
    missing = [
        item["expected_slug"]
        for item in QUERY_SUITE
        if item.get("expected_slug") and item["expected_slug"] not in slugs
    ]
    if missing:
        print(f"Missing expected fixtures in index: {missing}", file=sys.stderr)
        return 1

    results_a = run_suite(index_a, score_a, QUERY_SUITE)
    results_b = run_suite(index_b, score_b, QUERY_SUITE)
    decision = verdict(results_a, results_b, len(raw_a), len(raw_b))

    report = format_report(
        QUERY_SUITE,
        results_a,
        results_b,
        len(raw_a),
        len(raw_b),
        len(index_b),
        decision,
    )
    print(report)

    payload = {
        "corpus_docs": len(index_b),
        "index_bytes": {"A": len(raw_a), "B": len(raw_b)},
        "suite": QUERY_SUITE,
        "results_a": results_a,
        "results_b": results_b,
        "decision": decision,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_TXT.write_text(report, encoding="utf-8")
    print(f"Wrote {OUT_TXT.relative_to(ROOT)}")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
