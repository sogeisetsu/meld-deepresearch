# Genre: Comparison (对比选型)

Appends the following sections **after** `## Findings`, before the
renderer-owned `## Sources`. Use when the request is to compare options and
recommend one.

1. **Evaluation basis** — the need, the comparison dimensions and their weights
   (评估背景：需求 / 维度 / 权重). State the weights explicitly; they govern the
   recommendation.
2. **Option overview** — one short block per option (选项概览).
3. **Comparison matrix** — a Markdown table is **required** (对比矩阵). Rows are
   options, columns are the weighted dimensions; every cell that states a
   figure carries an inline citation marker.
4. **Per-dimension analysis** — one subsection per dimension, each citing its
   evidence (逐维度分析).
5. **Recommendation** — the pick and the reasoning, tied to the weights
   (综合建议).
6. **Risks & limits** — what the recommendation does not cover (风险与局限).

A comparison without the matrix is incomplete; the matrix is the spine of this
genre. Required sections are unchanged and always come first (draft stage; the
pre-delivery readability pass later dissolves them).
