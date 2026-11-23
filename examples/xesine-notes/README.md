# XeSINE-Net 项目结构示例

示例沿用 XeSINE-Net 的项目入口、独立文献笔记目录和 142–156 阶段编号。页面中的任务名和文字用于说明项目组织。

- [阶段索引](docs/init.md)
- [当前研究接力](当前研究接力.md)
- [文献与进展](文献与进展.md) · [文献笔记](文献笔记/README.md)
- [下一步](下一步.md)

## 项目目录

```text
XeSINE-Net/
├── README.md
├── 当前研究接力.md
├── 文献与进展.md
├── 下一步.md
├── 文献笔记/
├── docs/          项目阶段记录
├── code/          方法和分析代码
├── configs/       运行配置
├── research/      阶段研究材料
├── results/       结果记录
├── figures/       科研图
└── output/        交付文件
```

研究者在项目首页维护当前问题和接手入口。Obsidian 提供审阅视图，Zotero 通过项目分类和条目链接接入文献。Git 记录代码、配置和笔记的版本。适合自动化的步骤可以用 Snakemake 写明输入、依赖和产物。科研图、汇报和稿件从阶段页链接到相应的源文件与版本。

## 软件界面和交付文件

| 示例 | 界面或文件 |
| --- | --- |
| Obsidian 项目入口 | [阶段档案界面](previews/obsidian.png) |
| Zotero 文献分类 | [SEP 物理与传播文献分类截图](previews/zotero.png) |
| ohmyplt 项目流程图 | [预览](previews/workflow.png) · [PDF](figures/workflow.pdf) · [SVG](figures/workflow.svg) |
| PowerPoint 汇报页 | [可编辑 PPTX](output/项目组织示例.pptx) · [预览](previews/ppt.png) |
| LaTeX 稿件 | [源文件](output/project-layout.tex) · [编译后的 PDF](output/project-layout.pdf) |

## Git 与 Snakemake

本示例用 [Snakefile](Snakefile) 管理阶段索引。规则读取 `docs/` 下的编号笔记和 [索引配置](configs/stage-index.json)，检查判断页与证据页的互链，由 [脚本](code/build_stage_index.py) 写出 [阶段索引表](results/stage-index.tsv)。在本目录运行以下命令。

```sh
uv run --no-project --python 3.12 --with snakemake==9.27.0 python -X utf8 -m snakemake --cores 1 results/stage-index.tsv
```

[运行记录](previews/workflow.txt)来自独立的示例 Git 仓库。第一版索引从 `155` 开始，第二次提交把起始阶段改为 `142`。Snakemake 预演列出受影响的索引任务。
