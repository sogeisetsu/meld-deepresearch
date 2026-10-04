# Genre: Chronicle (时序还原 / 历史)

Appends the following sections **after** `## Findings`, before the
renderer-owned `## Sources`. Use for historical, humanities and
attribution-type questions where the timeline is the argument.

1. **Background & people** — period, place and the actors involved
   (背景与人物). This section **consumes `background` claims**: context is
   recorded as `kind: "background"` in `evidence.json` and is never promoted
   into a `key_finding`.
2. **Timeline** — the ordered sequence of events (时间线). Each dated node
   carries an inline citation; uncertain dates are labelled `unknown`.
3. **Key-node analysis** — why the pivotal moments matter (关键节点分析).
4. **Evidence & disputes** — what the sources disagree about and the grade of
   each disagreement (证据与争议); use the `已确认` / `存在争议` / `无法证实`
   grading from `report-template.md`.
5. **Conclusion & aftermath** — what follows and what remains open (结论与余波).
6. **Appendix** — optional chronology table, source notes (附录).

Attribution questions ("who did what") rarely have binary answers: state what
is confirmed, what is disputed and what cannot be established. Required
sections are unchanged and always come first.
