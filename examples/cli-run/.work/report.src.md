# Nimbus 2.0 adoption: what the evidence supports

> **Illustrative sample.** This is a synthetic example run used to exercise the
> tooling and CI. The subject is fictional and the URLs are placeholders
> (`example.org`); nothing here is real research about a real project.

- **Report type:** evidence-checked technology brief
- **Report date:** 2026-09-29
- **Scope:** the Nimbus project's 2.0 release, adoption and performance claims
- **Data cut-off:** 2026-09-29
- **Basis:** four sources opened directly, plus one first-hand check of a page

## Contents

- [Definitions and scope](#definitions-and-scope)
- [Executive summary](#executive-summary)
- [Release and packaging](#release-and-packaging)
- [Adoption](#adoption)
- [Why it grew](#why-it-grew)
- [Build-time performance](#build-time-performance)
- [Outlook](#outlook)
- [Sources](#sources)

## Definitions and scope

Nimbus is the fictional subject of this sample. Throughout the report, "stars"
means the project's public popularity counter on one hosting site, counted as
reported on a single date; "2.0" means the release published on 2026-03-14.
The window is the three months after that release. Anything outside this
window, or resting on a source this brief did not open, is out of scope and is
marked `unknown` where it matters.

## Executive Summary

- 2.0 shipped on 2026-03-14 with no runtime dependencies, and the project
  passed roughly 12,000 stars within three months [^s1] [^s2].
- The available evidence attributes that growth mainly to build-time wins
  rather than to marketing activity [^s2] [^s3] [^s4].
- However, the star figure is a single snapshot, so
  "adoption accelerated" may be partly an artifact of which snapshot was taken
  [^s2] — the curve's shape is `unknown`.
- Two limits qualify everything above: one snapshot instead of a time series,
  and a build-time comparison run on a single machine [^s2] [^s3].

## Release and packaging

Nimbus 2.0 was published on 2026-03-14 and ships with no runtime dependencies
[^s1]. A widely repeated claim that the release removed plugin support is
contradicted by the release notes and is not supported by the comparison
writeup [^s1] [^s3]. The release-notes page was read directly on 2026-09-29
[^o1].

## Adoption

The project passed 12,000 stars within three months of the release [^s2]. If
the recorded rate holds, it is projected to pass 20,000 stars by the end of
2026 [^s2]. However, the adoption figure is a single snapshot, not an archived
time series, so "adoption accelerated" may be partly an artifact of which
snapshot was taken [^s2]; how the curve actually shaped up is `unknown`. A
second limit is the source of the comparison: the same writeup reports both
the star count and its own growth narrative [^s2] [^s3].

## Why it grew

Growth is explained mainly by build-time wins rather than by marketing activity
[^s2] [^s3] [^s4]. How far that explanation generalises beyond one machine is
`unknown`: the comparison was run once, on a single machine, and no second
run has been reported [^s3].

## Build-time performance

The comparison writeup reports faster builds for 2.0 than for 1.x [^s3], and
the release notes list the optimisations behind them [^s1]. The absolute
numbers should be read as indicative rather than benchmarked, because the
measurement conditions were not published [^s3].

## Outlook

On the evidence opened here, 2.0 is a real release with real build-time gains
and a popularity counter that rose quickly [^s1] [^s2] [^s3] [^s4]. What stays
`unknown` is the shape of the adoption curve over time and whether the
build-time advantage holds on other machines [^s2] [^s3]; answering either
would need an archived time series and a second benchmark run.

## Sources
