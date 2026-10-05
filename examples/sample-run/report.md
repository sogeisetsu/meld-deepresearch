> Citation-annotated version with footnote markers: [report.cited.md](report.cited.md)

# Nimbus 2.0 adoption: what the evidence supports

> **Illustrative sample.** This is a synthetic example run used to exercise the
> tooling and CI. The subject is fictional and the URLs are placeholders
> (`example.org`); nothing here is real research about a real project.

**Subject:** Nimbus 2.0 release and adoption · **Scope:** release, adoption,
performance · **Data cut-off:** 2026-09-29 · **Compiled:** 2026-09-29 ·
**Basis:** four sources opened directly plus one first-hand check

## Contents

- [Executive summary](#executive-summary)
- [Findings](#findings)
- [Counter-evidence and limits](#counter-evidence-and-limits)
- [What remains unknown](#what-remains-unknown)
- [Sources](#sources)

## Executive Summary

Nimbus 2.0 shipped on 2026-03-14 with no runtime dependencies, and the
project passed roughly 12,000 stars within three months. The available
evidence attributes that growth mainly to build-time wins rather than to
marketing activity. Two limits qualify the picture: the star
figures are a snapshot rather than an archived time series, and the build-time
comparison rests on a single machine. A widely repeated claim that
2.0 removed plugin support is contradicted by the release notes.

## Findings

### Release and packaging

Nimbus 2.0 was published on 2026-03-14 and ships with no runtime dependencies
. The release-notes page answered successfully when checked on 2026-09-29
.

### Adoption

The project passed 12,000 stars within three months of the release. If
the recorded rate holds, it is projected to pass 20,000 stars by the end of
2026.

### Why it grew

Growth is explained mainly by build-time wins rather than by marketing activity
.

### Counter-evidence and limits

**Strongest counter-evidence:** the adoption figure is a single snapshot, not
an archived time series, so "adoption accelerated" may be partly an artifact of
which snapshot was taken. Treat the growth curve as `unknown`.

Two further disagreements belong here rather than in a chapter of their own: a
widely repeated claim that the 2.0 release removed plugin support is
contradicted by the release notes and is not supported by the comparison
writeup, and the build-time explanation is asserted more strongly
in the comparison writeup than its single-machine setup supports.

### What remains unknown

- No daily star history is publicly archived, so the shape of the growth curve
  is `unknown`; only snapshots are available.
- The build-time comparison uses a single machine and a warm cache, so how far
  the build-time explanation generalises is `unknown`.

## Sources

- Nimbus 2.0 release notes — https://example.org/nimbus/announcements/2-0 (primary, 2026-03-14)
- Nimbus adoption passes 12,000 stars — https://news.example.com/2026/06/nimbus-adoption (secondary, 2026-06-20)
- Build-time comparison: Nimbus and three alternatives — https://benchmarks.example.net/nimbus-vs-alternatives?utm_source=newsletter (secondary, 2026-05-02)
- Nimbus (software) — https://encyclopedia.example.org/wiki/Nimbus_(software) (tertiary, unknown)

## Observations

- checked the release-notes page from the documentation host (2026-09-29)
