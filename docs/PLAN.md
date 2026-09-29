# meld-deepresearch — 最终落地计划

> 本文件是本项目的**权威开发计划**（source of truth）。
> `AGENTS.md` 只放项目约定与指针；**所有实现细节、里程碑、借鉴来源都在这里**。
> 计划日期：2026-09-29 ｜ 状态：M2 已完成（M3 未开始）

---

## 1. 项目标识

| 项 | 值 |
|---|---|
| 仓库 | `github.com/sogeisetsu/meld-deepresearch` |
| 作者 | **sogeisetsu**（GitHub） |
| skill ID / 目录名 / 仓库名 | `meld-deepresearch`（三者一致；注意**不可缩写成 `meld`**，会撞 GNOME/meld 与 MELD 数据集） |
| License | MIT |
| 形态 | **单个可移植 Agent Skill**（`SKILL.md` + `references/` + `scripts/`） |
| 目标宿主 | 任意 Agent Skills 兼容宿主（opencode / Claude Code / Codex / Cursor / Copilot / Gemini CLI …） |
| 一句话定位 | 把模糊话题变成**可核验、逐条引用**的研究报告的**轻量**技能 |

查重结果（2026-09-29，GitHub）：`meld-deepresearch` total=0（干净）；`meld` 单独 total=2880（**勿用**）。发布前需再查一次 **skills.sh** 注册表 ID 占用。

---

## 2. 设计哲学（不可违背）

1. **纪律 > 编排。** 深研究的瓶颈是"结论能否回溯来源 + 有没有主动证伪"，不是 agent 数量。把纪律做成**硬约束**。
2. **轻量即可移植。** 单 skill；脚本纯 Python 标准库；**工具名中性**；兼容各宿主路径占位符。
3. **文件即真相。** 原始检索与结构化证据**落盘**，主上下文只留结论，避免上下文黑洞。
4. **能自检就不靠自觉。** 机械校验器当**硬门**（不通过不交付），替代"请务必引用"。
5. **两档而非三档。** `quick` / `normal`，**由问题自动判定**；不做 heavy 多角色编排。
6. **可核验优先于好看。** 每个数字可点到原始来源；查不到标 `unknown`，不装懂。
7. **主动证伪是义务。** 反方证据与矛盾检测是**硬要求**。
8. **单一事实源，零跨 skill 依赖。** skill 之间不能互相调用，因此绝不设计多 skill 联动。
9. **工具中立 + 能力分级。** 不写死工具名；能交互就先澄清，不能就写显式假设。
10. **中文可用、国际可读。** 英文正文；输出语言跟随用户。
11. **委派可选。** 宿主有子代理能力时**可以**按轴委派；没有就内联跑。**绝不强依赖子代理。**

> **"委派子代理"的准确定义**：skill 自己**不会、也不能**创建子代理；它只是在正文里**建议宿主 agent**调用其自身的 task/subagent 能力做上下文隔离，子代理用**文件（绝对路径）**回传结果。本 skill **默认内联**，委派仅作可选优化。

---

## 3. 决策记录（已定）

- ✅ License = **MIT**
- ✅ **只做 skill**，不做子代理 / 不保留薄壳
- ✅ 面向**开源**；作者 = **sogeisetsu**
- ✅ **含 scripts**
- ✅ 英文 `SKILL.md` + 英文 `references` + 英文 `description`（**description 纯英文，无中文触发词**）
- ✅ `SKILL.md` 含 **`metadata`** 块，写入 **author: sogeisetsu**
- ✅ 仓库含 **`.gitignore`**（初始化；并进入 `AGENTS.md` 的文件架构清单）
- ✅ 文件架构（repo layout）**必须实时更新**（见 `AGENTS.md`）
- ✅ 参考核心：**Weizhena/Deep-Research-skills + SenseNova-Skills**（MIT，可借鉴甚至复用文本），并博采其他大厂
- ✅ 两档 `quick`/`normal`，**根据用户问题自动选择**
- ✅ 反方证据 + 矛盾检测 = 硬要求
- ✅ 来源质量强制标 `primary/secondary/tertiary`
- ✅ 先澄清再研究（能交互问 1–3 问，否则写显式假设）
- ✅ 交付物：`report.md` + `sources.md` + `evidence.json` + `citations.json`
- ✅ 只做 Markdown 交付（不做 HTML/PPT）
- ✅ 脚本：`check_evidence.py` + `render_citations.py` + `dedupe_sources.py`
- ✅ 校验为**硬门**
- ✅ 发布走 `gh skill publish` + `npx skills add`
- ✅ Topics：`agent-skills` `skills-sh` `deep-research` `research`
- ✅ README 含"参考实现/致谢"章节；附 `CHANGELOG.md` + `NOTICE`
- ✅ 无模型配置问题（skill 用调用方模型）

---

## 4. 仓库结构

文件树已**独立建档**（逐个文件带注释、深度 2 层）：见 **[`FILE_TREE.md`](FILE_TREE.md)**。本节不再重复。

任何文件/目录的**新增、删除、改名或作用变更**，都必须同步更新该文件树。

---

## 5. 各文件内容计划

### 5.1 `SKILL.md`（English，入口，≤ ~200 行）

**frontmatter**
```yaml
name: meld-deepresearch
description: <英文，<=1024，含触发语义>
license: MIT
compatibility: Requires web search/fetch, file read/write and command execution; optional PDF, code and subagent capabilities.
metadata:
  author: sogeisetsu
  repository: https://github.com/sogeisetsu/meld-deepresearch
  version: 0.1.0
```

> `metadata` 为自由字段；opencode 只解释 `metadata.opencode/*`，其余键忽略。`author` 写 **sogeisetsu**。

**`description`（纯英文）要点**：systematic research、multi-source、competitive analysis、literature review、trend analysis、fact-checking、cited report；含"不要只搜几条就回答"的区分语。**不写中文。**

**正文章节**
1. When to use / not to use（排除：一句摘要、给定单来源整理、纯润色）
2. Capability probe —— Tier1 强制（read / write / exec / web search / web fetch）；Tier2 可选（PDF / code / social），缺失降级并告知
3. Request anchors —— `language`（跟随用户）、`format`（默认 `report`）、output dir
4. Clarify（≤1–3 问；不能交互则写显式 assumptions）
5. Tier selection → `references/tier-selection.md`
6. Workflow → `references/protocol.md`
7. Evidence & citation rules → `references/evidence-contract.md`
8. Budget & stop conditions
9. Self-check gate —— 跑 `check_evidence.py` + `render_citations.py`，不过不交付
10. Deliverables —— `report.md` + `sources.md` + `evidence.json` + `citations.json`
11. Failure & retry
12. Non-negotiables —— 不编造 / 主动 refute / 未知标 `unknown` / 无来源不结论
13. Context strategy（可选委派子代理）

### 5.2 `references/protocol.md`
见 §6 的机制细节。

### 5.3 `references/evidence-contract.md`
精简自商汤 sn-deep-research：
- `claims[]`：`id`(`dN.cM`) / `text` / `kind`(`factual`|`interpretive`|`projective`) / `polarity`(`support`|`refute`|`neutral`) / `topic_tag` / `answers_key_question`(`kqN`|null) / `evidence[]`
- `evidence[]`：`source_id` / `snippet` / `quote_type`(`direct`|`paraphrase`|`numeric`)
- `sources[]`：`id` / `url` / `title` / `quality`(`primary`|`secondary`|`tertiary`) / `published_at`
- `writing_context[]`：`id`(`dN.wM`) / `kind` / `text` / `source_ids[]` / `applies_to[]` / `use`
- `key_findings[]`：`finding` + `claim_ids[]`（派生综合，指回本文件 claim）
- 硬规则：`factual` 需 ≥1 `primary|secondary`；`projective` 需 ≥1 任意来源；`interpretive` 需 ≥2 个**不同** source；禁止规范性 claim

### 5.4 `references/tier-selection.md`
见 §6.2。

### 5.5 `references/report-template.md`
骨架：`# Title` → `## Executive Summary` → `## Findings`（逐条内联引用）→ `## Contradictions & Counter-evidence` → `## Gaps & Unknowns` → `## Sources`；附质量四维自检；写作规则：表述强度匹配证据强度、禁止规范性 claim。

### 5.6 `scripts/`（纯 Python 3 标准库）

**通用约定**：UTF-8 无 BOM；`python` / `python3` 均可；不联网、不装包；stdout 输出单个 JSON 对象；退出码 `0`（通过）/ `1`（校验失败）/ `2`（输入错误：文件不存在、JSON 非法、参数用法错误）。

**`check_evidence.py`**

```bash
python check_evidence.py <evidence.json> [--plan <plan.json>]
```

- 校验 `evidence-contract.md` 的结构、枚举、ID、引用完整性与硬规则 1–7。
- stdout：`{"ok": bool, "errors": [...], "warnings": [...]}`；每个条目为 `{"code": "...", "message": "...", "where": "..."}`。
- 错误码：`E_JSON`(→exit 2) / `E_SHAPE` / `E_EMPTY`(claims 或 sources 为空) / `E_ID_PATTERN` / `E_ID_UNIQUE` / `E_ENUM` / `E_REF_SOURCE` / `E_REF_CLAIM` / `E_REF_KQ` / `E_FACTUAL_SOURCE` / `E_INTERPRETIVE_TWO` / `E_PROJECTIVE_BASIS` / `E_NORMATIVE` / `E_PLAN_DIM_UNKNOWN` / `E_PLAN_DIM_UNCOVERED`。
- 警告码：`W_NO_REFUTE` / `W_NO_FINDINGS`(key_findings 为空) / `W_KQ_UNANSWERED`。
- `sources[].url` 只校验"非空且以 `http://` 或 `https://` 开头"；可达性**不**校验（不联网）。
- `interpretive` 的"两个不同来源"要求两个 `source_id` 的 `url` 字符串也不同（同一 URL 的两个 id 不算两个来源）。
- `E_NORMATIVE` 是**基于固定短语表的最佳努力启发式**，不是语义判定；短语表以 `evidence-contract.md` 为准。
- `applies_to[]` 只做模式校验（`dN` / `dN.cM`），不校验被引用对象是否存在。
- `--plan` 交叉检查：每条 claim 的轴 `dN` 必须存在于 `plan.json` 的 `dimensions[].id`（否则 `E_PLAN_DIM_UNKNOWN`）；每个 plan 维度必须有 ≥1 条 claim（否则 `E_PLAN_DIM_UNCOVERED`）；plan 声明的 `key_questions[].id` 若无 claim 认领 → `W_KQ_UNANSWERED`。

**`render_citations.py`**

```bash
python render_citations.py --report <report.src.md> --evidence <evidence.json> \
  --output <report.md> [--citations <citations.json>]
```

- 按**首次出现顺序**扫描 `[^source_id]` 标记 → 映射为 `1..N`。
- 正文内联替换为 `[N]`；把文档中 `## Sources` 标题之后的全部内容替换为生成的编号参考文献列表（无该标题则追加）。
- `citations.json`：`{"ok": bool, "citations": [{"number": 1, "source_id": "s1", "title": "…", "url": "…", "quality": "…", "published_at": "…"}], "orphans": [...], "uncited": [...]}`。
- stdout 摘要：`{"ok": bool, "citation_count": N, "orphans": [...], "uncited": [...]}`。
- **orphan**（标记指向 `sources[]` 中不存在的 id）→ `ok:false`、exit 1；**未解析**（渲染后仍残留 `[^` 或空 id 标记）→ 同样 `ok:false`、exit 1；**uncited**（evidence 中有来源但报告中从未引用）→ 仅警告。
- 默认 `--citations` 与 `--output` 同目录的 `citations.json`。

**`dedupe_sources.py`**

```bash
python dedupe_sources.py --evidence <evidence.json> --output <sources.md>
```

- URL 规范化：去首尾空白 → scheme/host 小写 → 去 `#fragment` → 去追踪参数（`utm_*`、`gclid`、`fbclid`、`ref`、`ref_src`）→ 去默认端口（http:80 / https:443）→ 去路径末尾单个 `/`（根路径除外）。
- 去重键 = 「剩余 query 参数排序后」的规范化 URL；展示保留首次出现的原始 URL；重复来源合并并记录被合并的 id。
- `sources.md`：按 `quality`（primary→secondary→tertiary）再按 `id` 排序的表格（id / title / quality / published_at / URL）。
- stdout：`{"ok": bool, "sources": N, "duplicates_merged": M}`。

**`plan.json`（normal 档计划文件）**

```json
{
  "tier": "normal",
  "dimensions": [
    {
      "id": "d1",
      "name": "…",
      "scope_ownership": "…",
      "source_classes": ["primary", "secondary"],
      "depth": "…",
      "time_sensitivity": "window | sensitive | stable",
      "key_questions": [{"id": "kq1", "text": "…"}]
    }
  ]
}
```

- `check_evidence.py --plan` 只依赖 `dimensions[].id` 与 `dimensions[].key_questions[].id`；其余字段为人类可读元数据，校验器忽略。

### 5.7 元文件
`package.json`、`README.md`（含 6 宿主安装矩阵 + 致谢）、`NOTICE`、`CHANGELOG.md`、`.gitignore`、`.github/workflows/validate.yml`。

### 5.8 `examples/` 与 CI 校验

- **`examples/sample-run/`**：一份**完整正例**（`report.src.md`、`evidence.json`、`report.md`、`sources.md`、`citations.json`），由脚本**实际生成**。主题为**示例性**内容（占位 URL，如 `example.org`），报告顶部必须注明 `illustrative sample`，避免被误当作真实研究结论。
- **`examples/invalid/`**：反例固定件——
  - `evidence.unknown-source.json` → `E_REF_SOURCE`
  - `evidence.tertiary-only.json` → `E_FACTUAL_SOURCE`
  - `evidence.single-source-interpretive.json` → `E_INTERPRETIVE_TWO`
  - `evidence.no-refute.json` → 仅 `W_NO_REFUTE`，`ok:true`、exit 0
  - `report.orphan.src.md` → render_citations 检出 orphan、exit 1
- **`.github/workflows/validate.yml`**：
  1. 规范检查——`name` ≤64 且小写 kebab；`description` ≤1024 且纯 ASCII（无中文）；`license: MIT`；`metadata.author: sogeisetsu`；`skills/` 内不得出现宿主专有工具名（`websearch` / `WebFetch` / `Task` / `AskUserQuestion`）与 POSIX-only 命令（`date +` / `cp -r` / `~/.config`）。
  2. 脚本自测——正例全部 exit 0；每个反例按**预期错误码**失败（exit 1）；`dedupe_sources.py` 在正例上 exit 0。

---

## 6. 运行机制（清晰版）

### 6.1 一次运行的完整时序（输入 → 动作 → 产物 → 门）

| # | 阶段 | 输入 | 具体动作 | 产物 | 决策 / 门 |
|---|---|---|---|---|---|
| 0 | **Capability probe** | 宿主环境 | 探测 read / write / exec / websearch / webfetch 是否可用 | 内存中的能力表 | Tier1 缺任一 → **暂停并提示用户**，不派发 |
| 1 | **Anchor** | 用户请求 | 定 `language`（跟随用户）、`format`（默认 `report`）、`output_dir` | 三个锚点（内存） | 无 |
| 2 | **Clarify** | 请求 | 能交互：问 1–3 个**只影响范围/时点/地域/口径**的问题；不能：写显式 `assumptions` | `assumptions` | 未答不阻塞，写假设继续 |
| 3 | **Tier select** | 请求 + assumptions | 按 §6.2 规则打分 | `tier = quick \| normal` | 命中任一 normal 条件即升档；用户可覆盖 |
| 4 | **Plan** | 请求 + assumptions | quick：内部生成 `kq1..kqn`；normal：生成 dims（含 `scope_ownership` / 来源类别 / `depth` / 时效） | quick：无文件；normal：`plan.json` | 维度必须**可独立启动、检索范围不重叠** |
| 5 | **Research**（循环） | plan / 请求 | 每维度：Search → URL 池 → Fetch → **读原文** → 评估 → 找缺口 → 再搜（≤3 轮） | `sub_reports/dN.evidence.json` | 达 `depth` 门槛即停 |
| 6 | **Merge** | `sub_reports/dN.evidence.json` | 合并四个顶层数组（`claims` / `sources` / `writing_context` / `key_findings`）为单一 `evidence.json` | `evidence.json` | 合并后 id 仍唯一；重复来源折叠为一条 |
| 7 | **Self-check ①**（硬门） | evidence | 跑 `check_evidence.py` | `{"ok":…}` | 不过 → 按错误一次性修复后重跑（≤1 次） |
| 8 | **Write** | 全部 evidence | quick/normal **一次成文**，逐条内联引用；禁止新事实 | `report.src.md` | 强度不得超证据 |
| 9 | **Render ②**（硬门） | `report.src.md` + evidence | 跑 `render_citations.py` | `report.md` + `citations.json` | 有 orphan/unresolved → 修后重跑（≤1 次） |
| 10 | **Sources** | evidence | 跑 `dedupe_sources.py` | `sources.md` | — |
| 11 | **Deliver** | — | 返回 4 件套路径 + 覆盖度/边界说明 | `report.md` `sources.md` `evidence.json` `citations.json` | 无 |

### 6.2 自动选档规则（tier-selection）

| 档位 | 判据（命中任一即该档；normal 优先于 quick） |
|---|---|
| **quick** | 单一自包含问题；一条研究线；≤3 个子问；无独立检索轴；用户要"简报/答案/单点核查" |
| **normal** | 存在 **≥2 条可独立检索的轴** ／ 需跨维度综合 ／ 实体对比 ／ 明确要报告或白皮书 ／ 预期证据冲突 |

默认 `quick`；命中任一 normal 条件即升档；**用户可显式覆盖**。

### 6.3 检索循环的精确规则（protocol.md 核心）

1. **Search 先于 Fetch**；没有候选 URL 不得直接抓取。
2. 维护**候选 URL 池**：合并 → 规范化 → 去重 → 按来源质量/相关性/时效排序。
3. **搜索摘要不得作为证据**；采信前**必须打开原文核对**。
4. **主动搜 refute**：反方、失败案例、不可证实主张（"refute 数量=0 通常意味着没好好搜"）。
5. **时效三情形**：① 任务限定时间窗 → 只在窗内取证；② 无限定但时效敏感 → 追最新，数字标时点；③ 稳定事实 → 优先现行来源。
6. 每轮评估：来源独立性 / 时效 / 可验证性，并判断是否饱和（达 `depth` 门槛即停）。

### 6.4 硬门（自检）
- **门 ①**：`check_evidence.py` 必须 `ok:true`（factual 缺一手来源、interpretive 缺第二独立来源 → 直接失败）。
- **门 ②**：`render_citations.py` 不得有 orphan / 未解析引用。
- 任一不过 → 修复后重跑；重跑仍不过 → 停止并如实报告，**不交付**。

### 6.5 预算与停止
- quick：≤ 8 次 fetch、≥ 5 个不同来源；normal：≤ 25 次 fetch、≥ 15 个来源；每轴最多 3 轮 Search→Fetch。
- **到预算即停，返回当前最优覆盖**，并显式标注未覆盖项（借鉴腾讯 Hyra"预算耗尽返回历史最优"）。
- 不无限循环。

### 6.6 失败与重试
plan / research / write / render 各上限 **1 次**；仍失败 → 停止，报告失败阶段 + artifact 路径 + 最后一轮错误，**不空转、不假装完成**。

### 6.7 产物与目录
- 目录：`meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`（可自定义 outdir）。
- 交付物：`report.md`、`sources.md`、`evidence.json`、`citations.json`。
- 中间产物：`plan.json`（normal 档）、`report.src.md`（成文草稿）、`sub_reports/dN.evidence.json`（分轴证据）。
- 宿主无写盘能力时：**只返回正文**，并说明未落盘。

---

## 7. 借鉴地图（清晰版）

### 7A. 按能力域（做什么 → 从谁借 → 落在哪）

**A. 证据与引用（硬纪律）**

| 能力 | 从谁借 | 具体做法 | 落在哪 |
|---|---|---|---|
| 三态断言 | 商汤 sn-deep-research | `factual` / `interpretive` / `projective` | `evidence-contract.md` |
| 立场 + 证伪义务 | 商汤 + 智谱 AutoGLM | `support`/`refute`/`neutral`；必须主动搜反方 | `evidence-contract.md` `protocol.md` |
| 引语类型纪律 | 商汤 | `direct`/`paraphrase`/`numeric`；摘要不算证据 | `evidence-contract.md` |
| 来源质量三档 | 商汤 + Salesforce EDR | `primary`/`secondary`/`tertiary`；factual 需 ≥1 一手/二手 | `evidence-contract.md` |
| 逐 claim 引用 | OpenAI / Perplexity / 商汤 | 每个数字可点回原始来源 | `report-template.md` |
| 口径与边界 | 商汤 `writing_context` + Kimi | 样本/方法/可得性缺口单独记录 | `evidence-contract.md` `report-template.md` |
| 综合层 | 商汤 `key_findings` | 派生综合，指回 claim_ids，不引入新事实 | `evidence-contract.md` |
| 表述强度匹配 | 商汤 review + 百度 RACE | 措辞不得强于证据 | `report-template.md` |

**B. 研究流程**

| 能力 | 从谁借 | 具体做法 | 落在哪 |
|---|---|---|---|
| 先澄清 | Kimi / Perplexity / OpenAI | 问 1–3 个只影响范围的问题 | `SKILL.md` |
| 可编辑计划 + HITL | Gemini / DeerFlow / Weizhena | 计划可被用户确认/修改 | `SKILL.md` |
| 多视角提问 | Stanford STORM | 视角矩阵，破单一视角盲点 | `protocol.md` |
| 分轴 + 范围归属 | 商汤 `scope_ownership` + Anthropic | 维度可独立、检索不重叠 | `tier-selection.md` `protocol.md` |
| Search→URL→Fetch→评估 | 商汤 + OpenAI ReAct | 先搜后取、读原文、候选池 | `protocol.md` |
| 迭代检索 / 反思 | Perplexity / Gemini / EDR | 发现缺口再检索，直到达阈值 | `protocol.md` |
| 缺口检测 | Salesforce EDR + 商汤 supplement | reflection 找知识缺口 | `protocol.md` |
| 时效策略 | 商汤 | 三情形（窗口 / 敏感 / 稳定） | `protocol.md` |
| 预算与停止 | xAI 步数上限 + 腾讯 Hyra | 到预算返回最优覆盖 | `protocol.md` `SKILL.md` |

**C. 报告产出**

| 能力 | 从谁借 | 具体做法 | 落在哪 |
|---|---|---|---|
| 报告骨架 | Weizhena + 全体 | 摘要/发现/矛盾/缺口/来源 | `report-template.md` |
| 质量四维自检 | 百度 RACE | 全面/洞察/遵循/可读 | `report-template.md` |
| 引用渲染 | 商汤 `sn-prepare-citations` | 脚注 → 编号 + `citations.json` | `render_citations.py` |
| 来源去重 | 商汤 | URL 规范化去重 | `dedupe_sources.py` |
| 未知显式化 | Kimi / EDR | 查不到标 `unknown`，不装懂 | `report-template.md` |

**D. 工程与可移植**

| 能力 | 从谁借 | 具体做法 | 落在哪 |
|---|---|---|---|
| 上下文隔离（可选委派） | Anthropic / 通义 / DeerFlow | 宿主支持则按轴委派，文件回传 | `protocol.md` |
| 文件即真相 / 中间落盘 | 通义 IterResearch / DeerFlow / Kimi | 证据落盘，主上下文只留结论 | `protocol.md` |
| 工具名中性 + 占位符 | 商汤 | 不写死 `websearch`；兼容 `${SKILL_DIR}` 等 | `SKILL.md` |
| 能力分级探测 | 商汤 | Tier1 强制 / Tier2 可选并降级告知 | `SKILL.md` |
| 机械校验硬门 | 商汤 + 199-biotech | validator 不通过不交付 | `check_evidence.py` |
| 轻量框架 + 宽动作空间 | **腾讯 Hyra（The Bitter Lesson）** | 框架尽量轻，不做重编排 | 设计哲学 |
| 评估器驱动迭代 | 腾讯 Hyra | 用评估反馈驱动下一轮 | `protocol.md` |

### 7B. 来源与许可一览

| 来源 | License | 借了什么（一句话） |
|---|---|---|
| OpenSenseNova/SenseNova-Skills（商汤，5.7k★） | MIT | 证据契约 + 校验器 + refute 义务 + 引用渲染（**核心**） |
| Weizhena/Deep-Research-skills（2.3k★） | MIT | 两阶段 + HITL + item×field 结构化 |
| OpenAI Deep Research | 产品 | Plan-Act-Observe、逐 claim 引用 |
| Anthropic multi-agent research | 产品 | 上下文隔离、归因代理 |
| Google Gemini Deep Research | 产品 | 可编辑计划 + 反思循环 |
| Microsoft Researcher Critique & Council | 产品 | 生成/评审分离 |
| Perplexity Deep Research | 产品 | 迭代检索 |
| xAI Grok DeepSearch | 产品 | scratchpad 汇总、步数上限 |
| Alibaba-NLP/DeepResearch（通义） | Apache-2.0 | IterResearch、Research-Synthesis |
| bytedance/deer-flow | MIT | Context Engineering、HITL 计划中断 |
| Moonshot Kimi（含 Kimi Code 产品设计） | 产品 | 澄清、筛选比例、未知处理 |
| 百度 千帆 DeepResearch | 产品 | RACE 质量四维 |
| 智谱 AutoGLM 沉思 | 产品 | 动态验证/自我修正 |
| stanford-oval/storm | Apache-2.0 | 多视角引导提问 |
| SalesforceAIResearch/enterprise-deep-research | 见仓库 | reflection 检测缺口、steering |
| assafelovic/gpt-researcher | Apache-2.0 | planner/executor/publisher |
| langchain-ai/open_deep_research | MIT | 极简可配置工作流 |
| 199-biotechnologies/claude-deep-research-skill | — | 来源可信度评分 + 验证 |
| **腾讯 混元 Hyra-1.0**（Hunyuan Research Agent，2026-07-21） | 见仓库 `Tencent-Hunyuan/hyra-results` | **递归自我改进 + The Bitter Lesson 轻量 Harness + 预算耗尽返回历史最优** |

> Weizhena 与商汤均为 MIT，**可有出处地复用文本**；其余产品/非 MIT 仓库**只借鉴机制、不抄文本**。所有引用登记进 `NOTICE`。
> 参考链接：商汤 <https://github.com/OpenSenseNova/SenseNova-Skills>；腾讯 Hyra <https://hy.tencent.com/research/hyra>。

---

## 8. 明确不做

- ❌ 子代理 / 薄壳（只做 skill）
- ❌ heavy 三档编排、9 角色工厂、进度 WebUI、PPT/HTML 交付
- ❌ 跨 skill 依赖（不绑定任何 `sn-search-*` 之类）
- ❌ 写死工具名 / POSIX-only 命令 / 指定模型

---

## 9. 验证计划

1. `examples/sample-run/` 放真实产物；CI 跑 `check_evidence.py`（正例 ok / 反例报错）+ `render_citations.py`（orphan 检测）。
2. 规范校验：`name≤64`、`description≤1024`、小写 kebab ID；`gh skill publish --dry-run`。
3. 可移植性 grep：不得出现 `websearch`/`WebFetch`/`Task`/`AskUserQuestion`；不得出现 `date +`/`cp -r`/`~/.config`。
4. 双宿主实测：`npx skills add sogeisetsu/meld-deepresearch` 装到 opencode + 再一个宿主（Claude Code 或 Codex），各跑一次 quick 与 normal。
5. Windows 实测 `python`/`python3` 回退与 UTF-8 无 BOM。

---

## 10. 里程碑（M0→M4）

| 里程碑 | 内容 | 完成判据 |
|---|---|---|
| **M0** ✅ | 仓库骨架 + `LICENSE`/`NOTICE`/`CHANGELOG.md`/`package.json`/`.gitignore` + `README.md` + 目录树 | 文件齐全；`AGENTS.md` 架构同步 |
| **M1** ✅ | 写 `SKILL.md` + 4 个 `references/` | frontmatter 合规（含 metadata.author）；正文 ≤ ~200 行；纯英文 |
| **M2** ✅ | 写 3 个脚本 + `examples/sample-run/` + CI | 脚本自测通过；正/反例都验证 |
| **M3** | opencode 装机实测（`~/.agents/skills/`）+ 第二宿主实测 + 修 | quick 与 normal 各跑通一次 |
| **M4** | `gh skill publish --dry-run` → 发布 + topics + tag `v0.1.0` | 发布成功、可 `npx skills add` 安装 |

**opencode 安装无需改配置**：skill 放到 `~/.agents/skills/meld-deepresearch/`（跨工具路径）或 `~/.config/opencode/skills/` 即被发现。

---

## 11. 风险 / 未验证

- 自动触发依赖 `description` 质量，需实测调优（中文提问走语义匹配，预期可行，但需实测）。
- "skill 委派子代理"在各宿主能力不一（有报告称 Claude Code 子代理不能加载 skill）→ 已降级为**可选**。
- 硬门脚本在无 Python 的宿主会失效 → 设计为**尽力而为 + 明确跳过提示**。
- `meld-deepresearch` 在 GitHub 干净，但 **skills.sh 注册表 ID 占用待查**（发布前查一次）。
- 腾讯 Hyra 细节主要来自官方页面/媒体，未逐层读其仓库代码。
- `gh skill publish` 的规范校验口径以发布时实测为准。

---

## 12. 下一步

按 M0 → M4 顺序开发。改文件后读回验证；改配置/不可逆操作前先备份并确认；**文件架构变更时同步更新本文 §4 与 `AGENTS.md`**。
