# meld-deepresearch

🌐 **中文** · [<kbd>English</kbd>](../README.md)

一个**轻量、可移植的 Agent Skill 家族**，把含糊的话题变成一份**可核查、每句话
都有出处的研究报告**。

仓库里有三个互相配合、又各自独立可装的 skill：核心研究流程
`meld-deepresearch`、表格分析 `meld-da`、学术检索 `meld-search-academic`。
没有框架。它们能在任何支持
[Agent Skills](https://agentskills.io) 开放标准的主机上运行—— opencode、
Claude Code、Codex、Cursor、GitHub Copilot、Gemini CLI 等等——也绝不会把你
绑死在某一家厂商身上。

> **状态：** `v0.3.0`（规模化重构：三 skill、四产物交付、软预算 + 两轮延长、
> 分层 CI）。skill 已经实现（`SKILL.md`、`references/`、`scripts/`），并由 CI
> 在精选示例上跑通，可以直接从本仓库安装。见 [`docs/PLAN.md`](../docs/PLAN.md)。

## 为什么还要再做一个深度研究 skill

多数 deep research 工具要么是笨重的多智能体框架，要么只是一层薄薄的 prompt。
`meld-deepresearch` 走的是中间那条路：

1. **靠纪律，不靠编排。** 质量来自可追溯的证据和主动证伪，而不是更多的
   agent。
2. **轻量、可移植。** 核心 skill 零运行时依赖（脚本只用 Python 标准库）；
   `meld-da` / `meld-search-academic` 需要的第三方包写在各自的
   `requirements.txt` 里、缺了就降级；不写死任何主机特有的工具名。
3. **文件才是事实来源。** 研究产物落到磁盘上，模型上下文里只留结论。
4. **用机械闸门代替良好意愿。** 校验器强制执行证据规则，可以让整轮运行失败。
5. **两档，不是三档。** `quick` / `normal`，根据问题自动选择，不做笨重的
   编排。
6. **可核查优先于漂亮。** 每条断言都能点开原文；任何未经核实的内容都会被标成
   `unknown`。
7. **证伪是强制动作。** 反证与矛盾必须主动去找，绝不能默认它们不存在。

它把开源界和大厂 deep research 里最好的想法（证据契约、来源质量分级、反驳义
务、带预算的停止条件、多视角提问）都吸收进来，浓缩成一个自包含的 skill。见
[`NOTICE`](../NOTICE) 和 `docs/PLAN.md` 第 7 节。

## 安装

这个 skill 就是一个目录，里面装着 `SKILL.md`、`references/` 和 `scripts/`。
用下面任意一种方式安装即可。

### 一行命令

```bash
# skills.sh / Vercel skills CLI（可安装到约 40 个受支持的主机）
npx skills add sogeisetsu/meld-deepresearch

# GitHub CLI（v2.90.0+），适用于 Copilot、Claude Code、Cursor、Codex、Gemini
gh skill install sogeisetsu/meld-deepresearch meld-deepresearch
```

### 手动安装（按主机）

把 `skills/` 下的三个目录（`meld-deepresearch/`、`meld-da/`、
`meld-search-academic/`）复制到你所用主机的 skills 目录；只用核心研究流程时，
复制 `meld-deepresearch/` 一个就够。跨工具的通用路径 `~/.agents/skills/` 已被
多个主机识别。

| 主机 | 全局 | 项目内 |
|---|---|---|
| opencode | `~/.agents/skills/` | `.opencode/skills/` |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.codex/skills/` 或 `~/.agents/skills/` | `.codex/skills/` |
| Cursor | — | `.cursor/skills/` |
| GitHub Copilot | `~/.copilot/skills/` 或 `~/.agents/skills/` | `.github/skills/` |
| Gemini CLI | `~/.gemini/skills/` 或 `~/.agents/skills/` | `.gemini/skills/` |

> 发现路径随主机和版本而变；如果 skill 没有出现，请查阅你所使用主机的文档。

不需要任何配置。skill 直接用宿主自己的模型，你不需要为它配置模型。

## 使用

直接提出你的研究需求就行。skill 通过自己的 `description` 亮相，当请求匹配时
按需加载（深度研究、系统调研、竞品分析、文献综述、趋势分析、事实核查、需要引
用的报告……）。

随后它会自动选档：

- **`quick`** ——一条自成一体的研究线（写一段简报、回答单个问题、核对某个
  点）。
- **`normal`** ——多个可以独立检索的维度、实体对比、完整报告，或者预期会出现
  互相冲突的证据。

你也可以显式指定档位。

### 产物

每次运行都会在
`meld-deepresearch-reports/YYYY-MM-DD-{slug}-{hex4}/` 下产出**四个产物**：

| 文件 | 是什么 |
|---|---|
| `report.md` | **交付给读者的阅读版**：没有角标，首行链接到引用版 |
| `sources.md` | 去重后的来源清单 |
| `evidence.json` | 结构化的断言、证据、来源与边界 |
| `citations.json` | 渲染器生成的引用映射表 |

`report.md` 与引用版由**同一次渲染**生成，编号一致，不会互相漂移；引用版
`report.cited.md` 只是中间产物，存进 `.work/`，不作为交付物。`.work/` 里还有
`plan.json`（normal 档）、草稿 `report.src.md` 和各维度的 `sub_reports/`。

如果宿主没有文件系统访问权限，报告会改为直接在对话里返回。

## 工作原理

```text
探测宿主能力
  -> 锚定语言 / 格式 / 结构 / 输出目录
  -> 澄清（1-3 个问题，或写下明确的假设）
  -> 选档 + 定长度档位（并记录"值不值得写长报告"的理由）
  -> 规划（normal：给每个研究维度命名）
  -> 研究循环：检索 -> URL 池 -> 抓取 -> 阅读 -> 评估 -> 缺口
     （预算耗尽但关键问题未清 -> 最多自动延长 2 轮，逐轮记入 run-log；
       2 轮后仍不清 -> 标成 uncertainty，绝不编结论）
  -> 合并各维度证据  ->  evidence.json
  -> 自检（硬闸门①：证据校验器）
  -> 写报告  ->  report.src.md（开头放报告头信息块：主题 / 范围 / 数据截止日 /
     日期 / 依据，并在标题下给出目录；「矛盾与反证」「未知与缺口」暂作独立章节）
  -> 草稿 / 引用版评审（章节顺序等结构性检查，只警告不失败）
  -> 交付前可读性重排：把「矛盾与反证」「未知与缺口」织进正文，不再单独成章
     （最强反证提示与每处 unknown 标记必须在重排后原样保留）
  -> 重跑全部闸门
  -> 渲染（硬闸门②：不得有孤儿或未解析引用）-> 同一次生成两份报告
     report.md（交付物，首行链接到引用版）+ report.cited.md（存入 .work/，中间产物）
     + citations.json
  -> 内容硬闸门 content_review.py --clean 判 report.md：运行故障词黑名单命中，
     或独立的 `## 矛盾与反证` / `## 未知与缺口` 章节残留 -> 失败
     （章节顺序等结构性检查已前移到草稿 / 引用版评审）
  -> 生成 sources.md（URL 归一化 + 去重）
  -> 交付 report.md + sources.md + evidence.json + citations.json
```

关键规则：先检索再抓取；没读过原文就不采信摘要片段；主动去找反证；尊重时效
性；预算耗尽按上面的延长规则处理，而不是无限循环下去。表格分析走
`meld-da`，学术 / 科史题材必须走 `meld-search-academic` 的论文路由。

## 环境要求

- 一个支持 Agent Skills 标准的主机。
- 具备网络检索与抓取能力。
- 文件读写与命令执行能力（脚本和产物需要用到）。
- Python 3（核心脚本仅用标准库），用于证据校验器、引用渲染器和来源去重工具；
  这些脚本无法执行时，运行会优雅降级，并在输出中说明这一点。
- `meld-da` / `meld-search-academic` 的分析与浏览器抓取需要第三方包，各自写在
  `requirements.txt`（可选层在 `requirements-optional.txt`）。缺包时它们退回
  标准库读取层 / 官方 API / 通用检索，不会中断运行。

## 参考与致谢

这个 skill 站在许多项目的肩上。完整的借鉴清单在 `docs/PLAN.md` 第 7 节，署名
列表在 [`NOTICE`](../NOTICE)。其中影响最明显的两个是：

- [SenseNova-Skills](https://github.com/OpenSenseNova/SenseNova-Skills)（MIT）
  ——证据契约、校验器和引用渲染。
- [Weizhena/Deep-Research-skills](https://github.com/Weizhena/Deep-Research-skills)
  （MIT）——两阶段流程与人工介入的检查点。

## 开发

- 面向 agent 的项目约定：[`AGENTS.md`](../AGENTS.md)
- 权威计划与里程碑：[`docs/PLAN.md`](../docs/PLAN.md)

在仓库根目录运行本地检查：

```bash
python skills/meld-deepresearch/scripts/check_evidence.py \
  examples/sample-run/evidence.json
```

完整的验证集合——正向示例，加上 `examples/invalid/` 里的负向用例——列在
[`AGENTS.md`](../AGENTS.md) 中，由 CI 在 `.github/workflows/validate.yml` 中
执行。

## 许可证

MIT。见 [`LICENSE`](../LICENSE)。

---

🌐 **中文** · [<kbd>English</kbd>](../README.md)
