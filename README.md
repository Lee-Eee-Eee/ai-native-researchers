<p align="center">
  <img src="docs/media/tools/ai-native-researchers.png" width="88" height="88" alt="">
</p>

<h1 align="center">“模型一代”研究者</h1>

<p align="center">
  <a href="README.en.md">English</a> ·
  <a href="#示例项目">示例项目</a> ·
  <a href="#安装">安装</a> ·
  <a href="LICENSE">Apache-2.0</a>
</p>

<p align="center">
  <a href="skills/ai-native-researchers/references/library-sync.md"><img src="docs/media/tools/zotero.png" width="24" height="24" align="middle" alt=""> Zotero 文献</a> &nbsp;
  <a href="skills/ai-native-researchers/references/review-vault.md"><img src="docs/media/tools/obsidian.svg" width="24" height="24" align="middle" alt=""> Obsidian 笔记</a> &nbsp;
  <a href="skills/ai-native-researchers/references/reproduction.md"><img src="docs/media/tools/git.svg" width="24" height="24" align="middle" alt=""> Git 版本</a> &nbsp;
  <a href="skills/ai-native-researchers/assets/snakemake-starter/"><img src="docs/media/tools/snakemake.svg" width="24" height="24" align="middle" alt=""> Snakemake 分析</a> &nbsp;
  <a href="https://github.com/Lee-Eee-Eee/ohmyplt"><img src="docs/media/tools/ohmyplt.png" width="24" height="24" align="middle" alt=""> ohmyplt 绘图</a>
</p>

人工智能已经开始改变科研的分工。以前一个课题能同时往几个方向做，很大程度上要看组里有多少人，谁能腾出空读文献、写程序、做实验。现在一个普通研究者也可以请模型沿着几条思路各做一轮，等看过结果，再决定精力花在哪里。从想试一试，到手里真的有结果可看，中间那段路短了不少。能在刚开始学做科研的时候碰上这场变化，我觉得很幸运。

我最在意的是，做研究的人得掌握自己的工作。几轮调研下来，书目和原文散在各段对话里。助手接着跑实验，改了几个条件，我想停下来判断一组新结果，就得先弄清它用过的数据和做过的对照。另开对话，我要把前面的事重新说一遍。合作者拿到代码和结果，也还得来问前几轮的决定。尤其现在可以更快地得到一批看起来不错的结果，自己就更得练会选问题、定对照，知道一份证据能说明到哪一步。

这样下去，实验室里怎么合作，研究成果怎么交给别人，都会跟着变。我先从自己每天要管的事做起，把这套办法整理成了 **AI-Native Researchers**。查过的论文进文库，实验每做一轮就留一份记录，代码和结果有各自的位置。助手往前做的时候，我能回来读进展，补判断，改下一步。合作者拿到项目，也从同一个首页接着做。这套工作流做成了一个可以安装的技能。 [研究者与助手的分工](skills/ai-native-researchers/references/model-generation.md)

「模型一代」这个名字来自蒋一凡和邓耿的两篇文章。 [蒋一凡《模型一代》](https://mp.weixin.qq.com/s?__biz=MzY5MzQ5NjgwNw==&mid=2247483674&idx=1&sn=facf9067217689d466efddf475190a59&chksm=f58d87e227d875dd4dbccbe0f66cb383fddcdcec95ac66a3f992d1cc87dcad1e71f021ad9d61#rd) · [邓耿《模型万代》](https://mp.weixin.qq.com/s?__biz=MzI0NjY1MDIwMQ==&mid=2247484921&idx=1&sn=ada6ae5a6af92849c49470672d803534&chksm=e8c21d1f61e9b6ccd0641eba378278df7a9cea53d2224a8ab931699635458abda2a5d1392afa#rd)

<p align="center">
  <img src="docs/media/research-workflow.png" width="780" alt="项目首页连接 Obsidian 笔记、Zotero 文献、Git 版本与 Snakemake 分析，并通向配图、汇报和论文。">
</p>

## 我用的办法

### <img src="docs/media/tools/zotero.png" width="22" height="22" alt=""> 文献和阅读笔记

AI 查完一批文献，我把核对过的条目按项目和用途收进 Zotero。用到一篇文章里的方法或结果，我就在阶段笔记留个链接，顺便记上章节或图号。过一阵再写稿，沿着笔记就找得回原文。整组书目和阅读笔记也可以同步到 Obsidian。 [文献同步](skills/ai-native-researchers/references/library-sync.md) · [ZotLit 批注](skills/ai-native-researchers/references/literature.md)

### <img src="docs/media/tools/obsidian.svg" width="22" height="22" alt=""> 实验记录和下一步

我请助手每做完一轮就补两份 Markdown。`001` 写做过的尝试、我对结果的判断和接下来的安排，`001a` 留结果表、异常样本和运行记录。我用 Obsidian 看这两份笔记，有意见就写在这轮的记录里。下一次开对话，我让助手先读首页和最近几轮的笔记。合作者拿到项目，也能沿着同一份记录往下读。 [在 Obsidian 审阅](skills/ai-native-researchers/references/review-vault.md)

### <img src="docs/media/tools/git.svg" width="22" height="22" alt=""> <img src="docs/media/tools/snakemake.svg" width="22" height="22" alt=""> 目录、版本和分析

几轮分析下来，目录里会积出好几版脚本、配置和结果。我希望用到一张图时，能顺着记录查到当时的数据和代码，所以原始数据、脚本和配置、分析结果、交付稿件各有各的位置。Git 记代码、配置和笔记的版本。数据和模型权重放在外部时，运行记录要写明位置和版本。多步分析用 Snakemake 写清每步的输入和输出，改了输入再跑，受影响的结果就会跟着更新。 [项目目录](skills/ai-native-researchers/references/project-structure.md) · [运行记录](skills/ai-native-researchers/references/reproduction.md) · [Snakemake 示例](skills/ai-native-researchers/assets/snakemake-starter/)

### <img src="docs/media/tools/ohmyplt.svg" width="22" height="22" alt=""> 从结果到组会和论文

到了组会或正式汇报，我从阶段记录挑要讲的结果，用 ohmyplt 从结果表画图，脚本也留着。汇报用 PowerPoint 或 Beamer，论文沿用项目的 LaTeX 模板和 Zotero 书目。最后把源稿、定稿和用到的图表链接回阶段记录。等到改稿，我从这儿接着找。 [ohmyplt](https://github.com/Lee-Eee-Eee/ohmyplt) · [科研图、汇报与论文](skills/ai-native-researchers/references/research-outputs.md)

## 接入已有项目

手上已经做了一段时间的项目，可以先把原来的 Markdown 笔记索引出来。迁移命令会在笔记目录生成 `init.md`，比如 `docs/init.md`。在原首页加上这个索引，再补上最近的进展、结果和稿件。项目内用相对链接，别人拿到目录就能沿着首页读。外部数据另外写好访问说明。 [项目目录与迁移](skills/ai-native-researchers/references/project-structure.md)

团队可以按原有的版本管理、集群调度和归档方式接入。 [工具选择](skills/ai-native-researchers/references/tool-choices.md)

## 示例项目

我用 **XeSINE-Net** 的目录做了一个例子，保留了 `142` 到 `156` 的阶段编号，给演示笔记另写了标题和内容。从首页能看到当前进展、下一步和文献链接。打开阶段记录 `142` 就能找到配套的 `142a`。源码、配置、结果和交付文件分别在 `code/`、`configs/`、`results/` 和 `output/`。 [查看 XeSINE-Net 项目结构](examples/xesine-notes/)

另有一张实际的 Zotero 界面，打开的是「SEP 物理与传播」分类。 [Zotero 截图](examples/xesine-notes/previews/zotero.png)

## 安装

在 Codex 里可以直接发送下面这条指令。

> 请从 Lee-Eee-Eee/ai-native-researchers 安装 skills/ai-native-researchers。

手动安装时，把 [skills/ai-native-researchers](skills/ai-native-researchers/) 整个子目录复制到 `~/.codex/skills/`。安装好后，可以开一个新对话，先交给助手一次实验的记录。

> 用 $ai-native-researchers 整理刚结束的实验。沿用现有目录，写一页阶段判断，链接对应的逐例结果和生成结果表的命令。

阶段收尾和迁移脚本使用 Python 标准库。本仓库用 Python 3.12 测试。运行阶段索引示例可通过 `uv` 安装示例固定的 Snakemake 版本。页首的工具按需要接入，重画流程图需要 ohmyplt、Matplotlib、Pillow 和 resvg-py。 [阶段索引示例](examples/xesine-notes/#git-与-snakemake) · [流程图脚本](docs/media/render_workflow.py)

[技能正文](skills/ai-native-researchers/SKILL.md)

## 许可

仓库自有代码和文档采用 Apache-2.0。第三方图标、商标及截图中的第三方内容适用各自的使用条款。 [许可证](LICENSE) · [图标来源](docs/media/tools/sources.md)
