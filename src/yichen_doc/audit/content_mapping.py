"""Map source units conservatively and keep lexical candidates unresolved."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict
from typing import Iterable

from .schemas import ContentUnit, MappingRecord, MappingStatus, normalize
from .semantic_matching import compact, conflict_signals, lexical_similarity


def windows(units: Iterable[ContentUnit], width: int = 80) -> list[dict]:
    """Fixed-width non-overlapping windows, matching the legacy QA denominator."""
    rows = []
    for unit in units:
        text = normalize(unit.text)
        if not text:
            continue
        if len(text) <= width:
            chunks = [(0, text)]
        else:
            chunks = [(i, text[i:i + width]) for i in range(0, len(text) - width + 1, width)]
            tail_start = chunks[-1][0] + width
            if tail_start < len(text):
                chunks.append((tail_start, text[tail_start:]))
        for offset, chunk in chunks:
            rows.append({"window_id": f"{unit.unit_id}:w{offset:06d}", "source_unit_id": unit.unit_id,
                         "source_locator": unit.locator, "offset": offset, "text": chunk})
    return rows


def map_document_windows(source: list[ContentUnit], target: list[ContentUnit], width: int = 80) -> list[dict]:
    """Reproduce the historical document-wide fixed-window screen with locators.

    This is retained only for reconciliation with old QA figures. It is not a
    semantic completeness score and the output labels every miss unresolved.
    """
    def flatten(units):
        parts, spans, cursor = [], [], 0
        for item in units:
            value = normalize(item.text)
            if not value:
                continue
            parts.append(value)
            spans.append((cursor, cursor + len(value), item))
            cursor += len(value)
        return "".join(parts), spans

    source_text, source_spans = flatten(source)
    target_text, target_spans = flatten(target)
    records = []
    for start in range(0, max(0, len(source_text) - width), width):
        chunk = source_text[start:start + width]
        target_start = target_text.find(chunk)
        hit = target_start >= 0
        source_locs = [u.locator for a, b, u in source_spans if a < start + len(chunk) and b > start]
        target_locs = [u.locator for a, b, u in target_spans if hit and a < target_start + len(chunk) and b > target_start]
        from .schemas import unit_id
        import hashlib
        digest = hashlib.sha256((source[0].file_sha256 if source else "").encode()).hexdigest()
        records.append({"window_id": f"W-{unit_id(digest, f'document-window-{start}', chunk)[2:]}",
                        "source_file": source[0].file if source else "", "source_offset": start,
                        "source_locator": ";".join(source_locs), "source_text": chunk,
                        "target_locator": ";".join(target_locs), "mapping_status": "RETAINED" if hit else "UNRESOLVED",
                        "match_method": "document_wide_exact_text_screen" if hit else "no_exact_window_hit",
                        "reviewer_status": "REVIEW_REQUIRED" if not hit else "AUTO_TEXT_HIT",
                        "notes": "Exact document-wide text window; this screen does not establish semantic retention."})
    return records


def _target_containing(source_text: str, targets: list[ContentUnit]):
    needle = normalize(source_text)
    # A short label or entity appearing somewhere in a report is not a
    # meaningful destination. Keep those as unresolved candidates.
    if len(needle) < 8:
        return []
    hits = [t for t in targets if needle in normalize(t.text)]
    if hits:
        return [hits[0]]
    # Preserve order and record cross-unit mapping when a source unit spans
    # adjacent target paragraphs. A joined match remains a candidate unless
    # exact source text is actually present in the concatenated target stream.
    joined = "".join(normalize(t.text) for t in targets)
    start = joined.find(needle)
    if start >= 0:
        end = start + len(needle)
        hits, cursor = [], 0
        for t in targets:
            value = normalize(t.text)
            next_cursor = cursor + len(value)
            if value and cursor < end and next_cursor > start:
                hits.append(t)
            cursor = next_cursor
        return hits
    return []


def map_units(source: list[ContentUnit], target: list[ContentUnit], *, candidate_threshold: float = 0.45,
              authorized_removals: dict[str, dict] | None = None) -> list[MappingRecord]:
    authorized_removals = authorized_removals or {}
    target_norm = defaultdict(list)
    target_punct = defaultdict(list)
    for t in target:
        n = normalize(t.text)
        if n:
            target_norm[n].append(t)
            target_punct[compact(t.text)].append(t)

    records: list[MappingRecord] = []
    for s in source:
        n = normalize(s.text)
        exact = target_norm.get(n, [])
        rewritten = target_punct.get(compact(s.text), []) if not exact else []
        hits = exact or rewritten or _target_containing(s.text, target)
        best_score = 0.0
        best: list[ContentUnit] = []
        if not hits and n:
            scored = sorted(((lexical_similarity(s.text, t.text), t) for t in target), key=lambda x: x[0], reverse=True)
            if scored:
                best_score, candidate = scored[0]
                if best_score >= candidate_threshold:
                    best = [candidate]
        destinations = hits or best
        if not destinations:
            decision = authorized_removals.get(s.unit_id, {})
            valid_authorization = (isinstance(decision, dict) and decision.get("reason") and decision.get("authorization")
                                   and decision.get("reviewer") and decision.get("reviewed_at"))
            status = MappingStatus.INTENTIONALLY_REMOVED if valid_authorization else MappingStatus.UNRESOLVED
            records.append(MappingRecord(s.unit_id, s.file, s.locator, s.text, target[0].file if target else "",
                                         mapping_status=status, match_method="no_match",
                                         reviewer_status="VERIFIED" if valid_authorization else "REVIEW_REQUIRED",
                                         reviewer=decision.get("reviewer", "") if valid_authorization else "",
                                         reviewed_at=decision.get("reviewed_at", "") if valid_authorization else "",
                                         authorization=decision.get("authorization", "") if valid_authorization else "",
                                         notes=decision.get("reason", "") if valid_authorization else "No target candidate found; disposition requires reviewer, timestamp, reason and authorization."))
            continue
        candidate = destinations[0]
        # Compare a source unit to the complete mapped target span. Comparing
        # it to just the first fragment of a SPLIT mapping creates false
        # number/negation conflicts when the rest of the sentence is in the
        # next target paragraph.
        candidate_text = " ".join(x.text for x in destinations)
        # Exact/normalized/substring matches preserve the source wording. A
        # short table cell may occur in many unrelated paragraphs, so do not
        # scan all those hits for negation tokens. Semantic tripwires apply to
        # the single best lexical candidate that needs review.
        signals = conflict_signals(s.text, candidate_text) if not (exact or rewritten or hits) else []
        if exact:
            status, method, score = MappingStatus.RETAINED, "exact", 1.0
        elif rewritten:
            status, method, score = MappingStatus.REWRITTEN, "normalized", 1.0
        elif hits and len(destinations) > 1:
            status, method, score = MappingStatus.SPLIT, "exact_concatenated_adjacent_units", 1.0
        elif hits:
            status, method, score = MappingStatus.RETAINED, "exact_substring", 1.0
        else:
            status, method, score = MappingStatus.UNRESOLVED, "lexical_candidate_only", round(best_score, 4)
        if signals:
            status = MappingStatus.CONFLICT
        records.append(MappingRecord(
            source_unit_id=s.unit_id, source_file=s.file, source_locator=s.locator, source_text=s.text,
            target_file=candidate.file, target_locator=";".join(x.locator for x in destinations), target_unit_id=";".join(x.unit_id for x in destinations),
            mapping_status=status, match_method=method, similarity_score=score,
            numeric_consistency="CONFLICT" if any("数字" in x for x in signals) else "CONSISTENT" if s.numbers else "NOT_APPLICABLE",
            citation_consistency="MISSING" if s.citations and not candidate.citations else "PRESENT" if s.citations else "NOT_APPLICABLE",
            reviewer_status="AUTO_VERIFIED_EXACT" if status == MappingStatus.RETAINED and method == "exact" and not signals else "REVIEW_REQUIRED",
            notes="; ".join(signals) if signals else ("Lexical similarity is a review candidate, not proof of semantic retention." if status == MappingStatus.UNRESOLVED else "")
        ))

    # Destination convergence alone does not prove a semantic merge: many
    # source table cells can legitimately map into one target table row, and
    # repeated text can appear in multiple source locations. MERGED therefore
    # requires an explicit human disposition in the mapping review ledger.
    return records


def apply_mapping_review(records: list[MappingRecord], review_path: str | None) -> list[MappingRecord]:
    if not review_path:
        return records
    import json
    from pathlib import Path
    data = json.loads(Path(review_path).read_text(encoding="utf-8"))
    decisions = {str(x.get("source_unit_id")): x for x in data.get("decisions", [])}
    by_id = {r.source_unit_id: r for r in records}
    for source_id, decision in decisions.items():
        if source_id not in by_id:
            continue
        status = str(decision.get("mapping_status", "")).upper()
        if status not in {x.value for x in MappingStatus}:
            continue
        record = by_id[source_id]
        reviewer, reviewed_at = decision.get("reviewer", ""), decision.get("reviewed_at", "")
        reason, authorization = decision.get("reason", ""), decision.get("authorization", "")
        if not reviewer or not reviewed_at:
            continue
        if status == MappingStatus.INTENTIONALLY_REMOVED.value and not (reason and authorization):
            continue
        if status in {MappingStatus.RETAINED.value, MappingStatus.REWRITTEN.value, MappingStatus.MERGED.value,
                      MappingStatus.SPLIT.value, MappingStatus.VISUALIZED.value} and not decision.get("target_locator"):
            continue
        if status == MappingStatus.CONFLICT.value and not reason:
            continue
        record.mapping_status = MappingStatus(status)
        record.target_locator = decision.get("target_locator", record.target_locator)
        record.target_unit_id = decision.get("target_unit_id", record.target_unit_id)
        record.reviewer_status = "VERIFIED"
        record.reviewer = reviewer
        record.reviewed_at = reviewed_at
        record.authorization = authorization
        if reason:
            record.notes = (record.notes + "; " if record.notes else "") + reason
    return records


def mapping_stats(records: list[MappingRecord], source_units: list[ContentUnit], target_units: list[ContentUnit], width: int = 80) -> dict:
    source_windows = windows(source_units, width)
    matched_windows = sum(1 for w in source_windows if any(w["text"] in normalize(u.text) for u in target_units))
    # Reproduce the historical document-wide window check as a separately
    # named comparator. It removes whitespace over the concatenated Markdown
    # and uses range(0, len(text)-width, width), matching the prior script's
    # denominator exactly. This is a text screen, not semantic retention.
    whole_source = normalize("".join(u.text for u in source_units))
    whole_target = normalize("".join(u.text for u in target_units))
    legacy_windows = [whole_source[i:i + width] for i in range(0, max(0, len(whole_source) - width), width)]
    legacy_matched = sum(1 for item in legacy_windows if item in whole_target)
    counts = Counter(str(r.mapping_status) for r in records)
    unresolved = sum(1 for r in records if str(r.mapping_status) in {"UNRESOLVED", "MISSING", "CONFLICT"}
                     or r.reviewer_status == "REVIEW_REQUIRED")
    unreviewed = sum(1 for r in records if r.reviewer_status == "REVIEW_REQUIRED")
    verified = sum(1 for r in records if r.reviewer_status in {"VERIFIED", "AUTO_VERIFIED_EXACT"})
    semantic_candidates = sum(1 for r in records if r.match_method == "lexical_candidate_only")
    return {
        "source_units": len(source_units), "target_units": len(target_units),
        "unit_status_counts": dict(counts),
        "fixed_window_width": width, "window_denominator": len(source_windows),
        "exact_window_matches": matched_windows,
        "exact_window_match_rate": round(matched_windows / len(source_windows), 4) if source_windows else None,
        "legacy_document_wide_window_screen": {
            "window_width": width,
            "source_normalized_characters": len(whole_source),
            "denominator": len(legacy_windows),
            "exact_matches": legacy_matched,
            "exact_match_rate": round(legacy_matched / len(legacy_windows), 4) if legacy_windows else None,
            "interpretation": "Historical whitespace-stripped document-wide text screen. Candidate hits do not prove semantic retention and must not be used as the only completeness check."
        },
        "unresolved_unit_count": unresolved,
        "unreviewed_unit_count": unreviewed,
        "reviewed_unit_count": sum(1 for r in records if r.reviewer_status == "VERIFIED"),
        "automatically_verified_exact_count": sum(1 for r in records if r.reviewer_status == "AUTO_VERIFIED_EXACT"),
        "verified_content_unit_count": verified,
        "verified_coverage": round(verified / len(records), 4) if records else None,
        "semantic_candidate_count": semantic_candidates,
        "semantic_candidate_rate": round(semantic_candidates / len(records), 4) if records else None,
        "numeric_conflict_count": sum(1 for r in records if r.numeric_consistency == "CONFLICT"),
        "citation_missing_count": sum(1 for r in records if r.citation_consistency == "MISSING"),
        "key_content_omission_count": None,
        "key_content_omission_limit": "Key-content criticality is not inferred from generic paragraph text; provide a claim/critical-content ledger for this count.",
        "candidate_similarity_is_not_retention": True,
        "interpretation": "Exact text matching is an automatic screen. Rewritten, split, merged, visualized, removed, unresolved and conflicting items require mapping evidence or reviewer disposition."
    }
