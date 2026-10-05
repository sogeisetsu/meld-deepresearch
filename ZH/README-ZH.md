# meld-deepresearch

🌐 **中文** · [<kbd>English</kbd>](../README.md)

一个可移植的 Agent Skill，把含糊的话题变成一份可核查、有引用
支撑的研究报告。它遵循 Agent Skills 开放标准（`SKILL.md`），
任何兼容的主机都能直接从路径加载它——不需要框架，也不绑定厂
商。本仓库提供三个互相配合的 skill：核心研究循环，加上两个可
选的能力 skill。

## 它能给你什么

- 每条断言都链接到一份真正打开过的来源；任何未经核实的内容都
  标为 `unknown`，绝不猜测。
- 反证是被主动去寻找的——矛盾与缺口会被如实报告，而不是被抹
  平。
- 三道硬闸门拦住糟糕的运行：`check_evidence.py` 校验证据契约，
  `render_citations.py` 拒绝孤儿或未解析的标记，
  `content_review.py --clean` 用四个错误码判阅读版失败：
  `E_RUNTIME_TERM`、`E_STANDALONE_SECTION`、
  `E_FAILURE_NARRATION`、`E_APPARATUS_LEAK`。
- 两档努力级别 `quick` 与 `normal`，根据问题选择、可手动覆盖
  ——不需要多智能体机制。
- 一次渲染器运行同时产出两份报告文件：`report.md`，即你交付出
  去的阅读版，以及带引用标注的 `report.cited.md`，它作为中间产
  物留在 `.work/`，不是交付物。
- 核心脚本只用 Python 3 标准库；skill 本身没有运行时依赖。
- 文件才是事实来源：产物落到磁盘上，模型上下文里只留结论。

## 本仓库的 skills

| 目录 | 用途 | 依赖 |
|---|---|---|
| `skills/meld-deepresearch` | 核心研究 / 证据 / 引用循环 | 无——Python 3 标准库 |
| `skills/meld-da` | Excel 与电子表格数据分析工作流（移植自 SenseNova-Skills `sn-da-excel-workflow`） | `requirements.txt` 中的可选 Python 包；缺包时按文档降级 |
| `skills/meld-search-academic` | 学术检索、论文阅读、引用树追溯（移植自 SenseNova-Skills `sn-search-academic`） | `requirements.txt`（外加 `requirements-optional.txt`）中的可选 Python 包；缺包时按文档降级 |

每个 skill 都能独立使用；它们只有在
[`references/protocol.md`](../skills/meld-deepresearch/references/protocol.md)
§2a 记载的交接点上才能互相调用。

## 快速开始

1. 把本仓库克隆到磁盘上任意位置。
2. 把你的主机指向它：主机通过读取 `skills/<name>/SKILL.md` 来
   加载 skill。各主机的 skill 目录列在你所用主机自己的文档里；
   项目内的 `skills/` 目录在多数主机上都能用。
3. 可选——能力 skill 需要安装其各自 `requirements.txt` 中列出
   的包。没有这些包，skill 会降级到文档记载的回退方案。
4. 开一个新会话，提出研究需求：一份带引用的报告、一次对比、一
   篇文献综述、一次事实核查。skill 的 `description` 负责匹配；
   没有任何需要配置的东西。
5. 从该次运行的输出目录里取走交付物（见**产物**）。

核心 skill 复用主机自己的检索、抓取、文件与命令能力；它不附带
任何密钥，也不存储任何凭据。

## 一次运行如何进行

```text
probe → clarify → tier → plan → per-axis research → merge → gate ①
     → write → draft review → readability weave → re-run gates
     → dual render → content gate → deliver
```

- **probe** —— 检查主机具备哪些能力；缺少某个阻塞性能力时终止
  运行并说明。
- **clarify** —— 最多三个问题，或者在无人可答时写下明确的假
  设。
- **tier** —— `quick`（一条自成一体的线程）或 `normal`（若干可
  独立检索的维度）。
- **plan** —— `normal` 运行会在 `plan.json` 中写明研究维度与关
  键问题。
- **per-axis research** —— 检索 → 打开原始页面 → 评估 → 补充池
  子，每个维度最多三轮；摘要片段永远不算证据。
- **merge** —— `merge_evidence.py` 把各维度的文件折叠成一份
  `evidence.json`。
- **gate ①** —— 对合并后的文件跑 `check_evidence.py`
  （`normal` 档还要加 `--plan`）；失败即终止运行。
- **write** —— 只依据已校验的证据写出一份草稿 `report.src.md`。
  它开头是头部信息块（主题 / 报告类型 / 范围 / 数据截止 / 依据）
  的项目符号列表——每条对应渲染后的一行，因为连续的 Markdown 行
  会并成一段——接着是一个竖排列表形式的目录：每行一条，每条都是
  描述性、有内容的标题，覆盖所有顶层章节，绝不用 `·` 串成一行。
  首个发现之前先有一节定义与范畴，通用的容器标题（`## Findings`、
  `## 主要发现`）会被换成有内容的标题。草稿中
  `## Contradictions & Counter-evidence` 与 `## Gaps & Unknowns`
  保持独立成节，以便草稿评审检查它们。
- **draft review** —— 只警告的结构性检查（章节顺序与预期章节）
  跑在草稿 / 引用版上。
- **readability pass** —— 纪律材料在任意标题层级织进正文：
  `## Contradictions & Counter-evidence`、`## Gaps & Unknowns`、
  `## Observations` 以及 `### Counter-evidence and limits` /
  `### What remains unknown` 这类 H3 替身不得出现在交付的报告里；
  最强反证提示与每一处 `unknown` 标记必须在织入之后保留下来。
- **re-gate** —— 每道闸门在织入后的草稿上重跑一次。
- **dual render** —— 一次 `render_citations.py` 运行（闸门②）同
  时产出两份文件：`report.cited.md` 进入 `.work/`，它去掉标记的
  孪生兄弟 `report.md` 落在顶层：首行指针 → 头部信息块 → 目录 →
  正文 → `## Sources`。阅读版从不带 `## Observations` 一节——观
  测记录留在 `evidence.json` 和 `.work/report.cited.md` 里。
- **content gate** —— 对 `report.md` 跑
  `content_review.py --clean`，即交付闸门：四个错误码时退出码
  1——`E_RUNTIME_TERM`（运行故障术语）、`E_STANDALONE_SECTION`
  （H2 或 H3 层级的独立纪律章节，中英皆算，含
  `## Observations`）、`E_FAILURE_NARRATION`（告诉读者某个页面需
  要登录或打不开——那属于 `observations[]`/`gaps[]`），以及
  `E_APPARATUS_LEAK`（正文出现 skill id、文件名、协议或工具名；
  首行指针是唯一获准的例外）。只警告不失败：`W_PROSE_RATIO`、
  `W_NO_TOC`、`W_THIN_TOC`、`W_NO_INFO_BLOCK`、
  `W_NO_UNCERTAINTY`、`W_NO_DEFINITIONS`、`W_GENERIC_HEADING`、
  `W_APPARATUS_LEAK`、`W_RUNTIME_TERM`。章节顺序的结构性检查已
  经在草稿评审中跑过。
- **deliver** —— `dedupe_sources.py` 写出去重后的 `sources.md`，
  然后报告完整的产物清单，包括缺口与抓取失败。

每道闸门最多有一次修复后重试的机会；第二次失败会终止运行，并如
实报告，而不是交付出去。

## 产物

默认目录 `meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/`
（用户提供的路径会完全取代这个命名）：

| 文件 | 内容 |
|---|---|
| `report.md` | **交付物**——无标记的阅读版：首行指针 → 头部信息块 → 目录 → 正文 → `## Sources`；它从不带 `## Observations` 一节 |
| `sources.md` | 去重后的来源清单 |
| `evidence.json` | 合并后、通过闸门校验的证据，支撑每一条断言 |
| `citations.json` | 把标记链接到其来源的引用映射表 |

与它们并排的 `.work/` 存放中间产物：`plan.json`（normal 档）、
渲染前的草稿 `report.src.md`、同一次渲染产生的带引用标注的
`report.cited.md`（中间产物，不是交付物），以及各维度的
`sub_reports/`。

## 何时该用 / 何时不该用

**该用的时候**：答案必须建立在不止一份来源之上、并且可核查：格局
或趋势扫描、竞品对比、文献综述、事实核查，以及任何明确要求带引
用的报告或简报。

**不该用的时候**：一个直接回答就够：定义、一行就能查到的问题、整
理你已有的来源、纯改写或翻译，或者本就不期待证据的观点文章。

## 环境要求

- 一个实现了 Agent Skills 标准（`SKILL.md`）的主机。
- 网络检索、页面抓取、文件读写与命令执行能力；当可选能力缺失时
  skill 会优雅降级，并在输出中说明。
- 运行闸门与渲染器需要 Python 3（核心 skill 只用标准库）。

## 文档

- Skill 入口：[`skills/meld-deepresearch/SKILL.md`](../skills/meld-deepresearch/SKILL.md)
- 协议、预算、闸门：[`references/protocol.md`](../skills/meld-deepresearch/references/protocol.md)
- 证据 schema：[`references/evidence-contract.md`](../skills/meld-deepresearch/references/evidence-contract.md)
- 带注释的文件树：[`docs/FILE_TREE.md`](../docs/FILE_TREE.md)
- 开发计划与里程碑：[`docs/PLAN.md`](../docs/PLAN.md)

## 验证

完整的验证集合——正向示例、负向示例以及每一种渲染模式——列在
[`AGENTS.md`](../AGENTS.md) 中，并由 CI 执行。

## 许可证与署名

MIT——见 [`LICENSE`](../LICENSE)。作者：**sogeisetsu**。
[`NOTICE`](../NOTICE) 列出了所有其材料被移植或借鉴的上游项目，
包括两个 SenseNova-Skills 移植。

---

🌐 **中文** · [<kbd>English</kbd>](../README.md)
