# Nimbus 2.0 adoption: what the evidence supports

> **Illustrative sample.** This is a synthetic example run used to exercise the
> tooling and CI. The subject is fictional and the URLs are placeholders
> (`example.org`); nothing here is real research about a real project.

## Executive Summary

Nimbus 2.0 shipped on 2026-03-14 with no runtime dependencies [^1], and the
project passed roughly 12,000 stars within three months [^2]. The available
evidence attributes that growth mainly to build-time wins rather than to
marketing activity [^2] [^3] [^4]. A widely repeated claim that 2.0 removed
plugin support is contradicted by the release notes [^1] [^3]. Two limits
qualify the picture: the star figures are a snapshot rather than an archived
time series, and the build-time comparison rests on a single machine [^2]
[^3].

## Findings

### Release and packaging

Nimbus 2.0 was published on 2026-03-14 and ships with no runtime dependencies
[^1]. The release-notes page answered successfully when checked on 2026-09-29
[^o1].

### Adoption

The project passed 12,000 stars within three months of the release [^2]. If
the recorded rate holds, it is projected to pass 20,000 stars by the end of
2026 [^2].

### Why it grew

Growth is explained mainly by build-time wins rather than by marketing activity
[^2] [^3] [^4].

## Contradictions & Counter-evidence

**Strongest counter-evidence:** the adoption figure is a single snapshot, not
an archived time series, so "adoption accelerated" may be partly an artifact of
which snapshot was taken [^2]. Treat the growth curve as `unknown`.

A widely repeated claim that the 2.0 release removed plugin support is
contradicted by the release notes and is not supported by the comparison
writeup [^1] [^3].

## Gaps & Unknowns

- No daily star history is publicly archived, so the shape of the growth curve
  is `unknown`; only snapshots are available [^2].
- The build-time comparison uses a single machine and a warm cache, so how far
  the build-time explanation generalises is `unknown` [^3].

[^1]: Nimbus 2.0 release notes — https://example.org/nimbus/announcements/2-0 (primary, 2026-03-14)
[^2]: Nimbus adoption passes 12,000 stars — https://news.example.com/2026/06/nimbus-adoption (secondary, 2026-06-20)
[^3]: Build-time comparison: Nimbus and three alternatives — https://benchmarks.example.net/nimbus-vs-alternatives?utm_source=newsletter (secondary, 2026-05-02)
[^4]: Nimbus (software) — https://encyclopedia.example.org/wiki/Nimbus_(software) (tertiary, unknown)

[^o1]: checked the release-notes page from the documentation host — Windows 11, curl 8.9.1 (captured 2026-09-29)
