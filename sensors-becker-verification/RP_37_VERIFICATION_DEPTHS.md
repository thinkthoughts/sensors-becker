# RP_37 Verification Depths — Evidence Note

Records what the RP_37 verification implementation actually established, for `specification-grammar` to draw on later. This is an evidence artifact, not a proposal — it doesn't say what SG-6 should become, only what was observed.

## Three depths, as implemented and run

**V1 — artifact structure.** Pre-existing in `NB_00_RP_37_SOURCE_EXTRACTION.ipynb` before this work. Checks that generated files exist, are non-empty, have the expected dialogue count per stage, and that `identity.stage` matches the filename. Says nothing about whether the content is correct — only that the pipeline produced well-formed output.

**V2 — source-page content presence.** Added this session. For each of 18 extractions, checks that the cited page of the source PDF actually contains the claimed value: an exact digit-bounded match for single numbers, all embedded numbers checked individually for compound values (e.g. "1% in 2 minutes"), case-insensitive substring match for qualitative values (e.g. "negligible"). All 18 pass against the real PDF.

Worth being precise about what this does and doesn't establish, since it's easy to overstate: finding "140" on page 12 is evidence the citation is real, not proof the surrounding sentence was interpreted correctly. V2 is a citation-presence check, not a semantic-correctness check. The distinction matters because the numbers could in principle appear on the page in an unrelated context and still pass; nothing here rules that out. For RP_37 specifically, manual reading of the cited pages (done separately, in `SENSORS_BECKER_SG_AUDIT.md`) confirmed the surrounding context does support each claim — but that confirmation was manual, not something V2 itself performs.

**V3 — cross-artifact metadata consistency.** Added this session. Checks that a downstream artifact's repeated source metadata (author, organization) matches the canonical `SOURCE` dict. This is the depth that actually caught real errors: the known "Idaho National Laboratory" mismatch (now an explicit regression test — the check must fail against a synthetic copy of the original broken text, or the checker itself is considered broken) and a second, previously unnoticed "Daniel Becker" vs. "Dan Becker" mismatch, found on the first live run and fixed the same way.

## What's genuinely new here versus SG-6 as currently written

SG-6 (as revised after the sensors-becker pressure test) distinguishes structural verification from content verification — two depths. What RP_37 actually produced is three, and V2 and V3 are not the same kind of "content" check: V2 checks a claim against its original source; V3 checks one artifact against another artifact's own canonical data, with no reference to the original source at all. A specification could pass V2 and fail V3 (a correctly-extracted claim, misquoted downstream) or, in principle, fail V2 and pass V3 (an extraction that misquotes the source but is at least quoted consistently everywhere downstream) — they check different failure modes.

## What this note deliberately does not do

It does not propose that SG-6 should now say "there are exactly three verification depths." One implemented example is not enough evidence for a fixed count, the same caution that applied to extracting SG-1 through SG-7 from only three MB specimens. This note is offered as evidence for whoever next revises SG-6, not as the revision itself.
