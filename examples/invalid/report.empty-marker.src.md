# Nimbus 2.0 empty-marker check

> **Illustrative sample.** Synthetic CI fixture used to exercise blank
> citation-marker detection; nothing here is real research about a real project.

## Findings

The 2.0 release shipped on 2026-03-14 with no runtime dependencies [^s1], but
this draft also contains an empty marker [^] and a whitespace-only marker
[^ ]. Neither carries an id, so they can be neither numbered nor substituted —
gate ② must fail this draft even though the valid marker resolves.

## Sources
