# AI Native Researchers

让 AI 接手一个科研项目时，能沿着一条结论找到原始结果、运行方法和引用的论文。适合会反复改方法、做对照、写阶段报告的个人或小组。

给助手一句话就可以开始：

> 用 $ai-native-researchers 整理刚结束的实验。两种方法在哪些样本上有差别？把逐例结果连到阶段笔记，留下能重跑这一张表的命令。沿用我现在的目录。

在 Obsidian 里读阶段结论和逐例证据，在 Zotero 里找原文及批注，在 Git 里追踪代码和参数。已有多步计算时，Snakemake 负责按输入和输出的依赖重跑。普通 Markdown 编辑器也能打开所有项目笔记。技能默认用文件、CLI 和本地 API 在后台工作。

## 安装

仓库中可安装的技能位于 [skills/ai-native-researchers](skills/ai-native-researchers/)。用 Codex 的技能安装器时，可以直接说：

> 请从 Lee-Eee-Eee/ai-native-researchers 安装 skills/ai-native-researchers。

手动安装可以将这个子目录完整复制到 `~/.codex/skills/`，然后在新会话中使用 `$ai-native-researchers`。只做阶段记录时无需安装 Snakemake 或 ZotLit。

## 先跑一个小例子

克隆本仓库后，用 Python 3.12 从仓库根目录运行一条命令。目标选一个新目录，首次运行可能需要联网安装固定版本的 Snakemake。

```sh
python examples/demo.py research-demo
```

打开 `research-demo/README.md`，沿着首页看一项完整的小实验。两组传感器一共 7 条合成观测，B 组有一条缺测，另外两次读数并列最高。脚本先检查数据，再计算两组各自第一次达到实测峰值的时刻，最后把实际结果、证据和复算入口写回项目。你可以在阶段页加一句自己的判断，再运行同一条命令检查批注是否保留。

要套用到自己的计算，可复制[合成观测工作流](skills/ai-native-researchers/assets/snakemake-starter/)。已有结果表也可直接用[证据清单脚本](skills/ai-native-researchers/scripts/evidence.py)记录文件指纹。

## 日常怎么用

| 手头的问题 | 技能会留下什么 |
| --- | --- |
| 项目做到哪儿了？ | 一张首页，链接最近一次有结果的实验以及下一步要回答的问题 |
| 为什么相信这项结果？ | 一对阶段笔记，结论页讲判断，证据页链接输入、逐例输出和运行命令 |
| 这篇论文支持哪一句话？ | 项目笔记中的出处、Zotero 条目和可核对的章节或图表 |
| 换了输入，哪张表需要更新？ | 一条从原始文件通到目标表的 Snakemake 工作流 |

要把数字写回自己的项目，助手可以读本轮输出并填好阶段描述，然后执行[自动收尾命令](skills/ai-native-researchers/references/automation.md)。脚本从原编号接着排，让首页、判断、逐例表和文件指纹互相连通。重复执行会保留研究者的手写批注。完整做法见[技能正文](skills/ai-native-researchers/SKILL.md)。

## 模型一代研究者怎么工作？

研究者先说清想分辨的两种解释，以及什么观测会让自己改变判断。助手据此准备对照、运行分析、找出不符合预期的样本，把结论接回原始证据。换一个人接手时，他既能重复计算，也能看出上一次为什么作这个决定。

[研究者与模型的分工](skills/ai-native-researchers/references/model-generation.md)给出从选题到发表的完整例子。[工具选择表](skills/ai-native-researchers/references/tool-choices.md)按实际问题介绍数据版本、环境锁定、集群作业、实验追踪、书目检索和带 DOI 的成果归档。
