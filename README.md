# “模型一代”研究者

[English](README.en.md) · [示例项目](#示例项目) · [安装](#安装)

这几年我在学做科研，也在学着和 AI 一起做事。我请助手查论文、跑分析，准备组会时常要回聊天记录里找一篇已经查过的论文。实验做了几轮，代码和结果都在项目目录里，当时定下的对照条件和改参数的理由散在几段对话里。另开对话或合作者接手，我得把这些事再讲一遍。

我想把这些事留在项目里。打开首页，我就能找到读过的论文、每轮实验的记录和交出去的稿件。助手做完一轮，我在这里看进度、调整下一轮的方案。合作者也从同一页接手。我把这套做法整理成了 **AI-Native Researchers**，一项可以安装的科研项目管理技能。 [研究者与助手的分工](skills/ai-native-researchers/references/model-generation.md)

项目的名字来自两篇文章。蒋一凡写 AI 到来以后，身边的人重新考虑自己的学业和工作。邓耿把话题接了下去，谈到人得自己决定什么值得做。 [蒋一凡《模型一代》](https://mp.weixin.qq.com/s?__biz=MzY5MzQ5NjgwNw==&mid=2247483674&idx=1&sn=facf9067217689d466efddf475190a59&chksm=f58d87e227d875dd4dbccbe0f66cb383fddcdcec95ac66a3f992d1cc87dcad1e71f021ad9d61#rd) · [邓耿《模型万代》](https://mp.weixin.qq.com/s?__biz=MzI0NjY1MDIwMQ==&mid=2247484921&idx=1&sn=ada6ae5a6af92849c49470672d803534&chksm=e8c21d1f61e9b6ccd0641eba378278df7a9cea53d2224a8ab931699635458abda2a5d1392afa#rd)

![项目首页居中，左侧是 Obsidian 和 Zotero，右侧是 Git 和 Snakemake，下方是 ohmyplt 配图、PowerPoint 汇报和 LaTeX 稿件。](docs/media/research-workflow.png)

## 研究流程

### <img src="docs/media/tools/zotero.png" width="22" height="22" alt=""> 文献和阅读笔记

AI 帮我查完文献后，我把核对过的书目收进 Zotero 的项目分类。写阶段笔记时，我把用到的论文链接进去，顺手记下相关的章节或图号。后来要用同一张图，我可以从笔记回到原文。我也可以把 Zotero 分类里的书目和阅读笔记同步到 Obsidian。 [文献同步](skills/ai-native-researchers/references/library-sync.md) · [ZotLit 批注](skills/ai-native-researchers/references/literature.md)

### <img src="docs/media/tools/obsidian.svg" width="22" height="22" alt=""> 实验记录和下一步

一轮实验结束后，我请助手补两页 Markdown，在 `001` 记下本轮的尝试、我的判断和下一步，在 `001a` 附上结果表和运行记录，再记下异常样本。我在 Obsidian 看这两页，直接在相关处补意见。下次开新对话，我请助手先读项目首页和最近一轮的笔记。 [在 Obsidian 审阅](skills/ai-native-researchers/references/review-vault.md)

### <img src="docs/media/tools/git.svg" width="22" height="22" alt=""> <img src="docs/media/tools/snakemake.svg" width="22" height="22" alt=""> 目录、版本和分析

我在项目里分开存原始数据、代码和配置、分析结果、交付稿件，用 Git 留下代码、配置和笔记的版本。数据或模型权重放在别处时，我请助手在运行记录里写下位置和版本。分析有好几步时，我用 Snakemake 把每步的输入和产物写进规则。输入有变动，我再运行 Snakemake，让它更新依赖这份输入的结果。 [项目目录](skills/ai-native-researchers/references/project-structure.md) · [运行记录](skills/ai-native-researchers/references/reproduction.md) · [Snakemake 示例](skills/ai-native-researchers/assets/snakemake-starter/)

### <img src="docs/media/tools/ohmyplt.svg" width="22" height="22" alt=""> 从结果到组会和论文

准备汇报时，我从阶段笔记挑结果，用 ohmyplt 从结果表画图，再把图放进 PowerPoint 或 Beamer。论文用项目的 LaTeX 模板和 Zotero 书目。我在阶段笔记里附上源稿、定稿和图表的链接，改稿时再从这页打开当时的文件。 [ohmyplt](https://github.com/Lee-Eee-Eee/ohmyplt) · [科研图、汇报与论文](skills/ai-native-researchers/references/research-outputs.md)

## 接入已有项目

整理旧项目时，我先在原目录生成 `docs/init.md`，给已有的 Markdown 笔记做个索引。我从首页链接这份索引，再补上当前进展、结果和稿件。项目里的链接用相对路径。合作者拿到共享的目录和数据说明，可以从首页找到手头要接的工作。 [项目目录与迁移](skills/ai-native-researchers/references/project-structure.md)

团队原来用的版本管理、集群调度和归档工具可以继续用。 [工具选择](skills/ai-native-researchers/references/tool-choices.md) · [图标来源](docs/media/tools/sources.md)

## 示例项目

我用 **XeSINE-Net** 的目录做了一个例子，保留了 `142` 到 `156` 的阶段编号，给演示笔记另写了标题和内容。从首页能看到当前进展、下一步和文献链接。打开阶段记录 `142` 就能找到配套的 `142a`。源码、配置、结果和交付文件分别在 `code/`、`configs/`、`results/` 和 `output/`。 [查看 XeSINE-Net 项目结构](examples/xesine-notes/)

另有一张实际的 Zotero 界面，打开的是「SEP 物理与传播」分类。 [Zotero 截图](examples/xesine-notes/previews/zotero.png)

## 安装

在 Codex 里可以直接发送下面这条指令。

> 请从 Lee-Eee-Eee/ai-native-researchers 安装 skills/ai-native-researchers。

手动安装时，把 [skills/ai-native-researchers](skills/ai-native-researchers/) 整个子目录复制到 `~/.codex/skills/`。安装好后，可以开一个新对话，先交给助手一次实验的记录。

> 用 $ai-native-researchers 整理刚结束的实验。沿用现有目录，写一页阶段判断，链接对应的逐例结果和生成结果表的命令。

[技能正文](skills/ai-native-researchers/SKILL.md)
