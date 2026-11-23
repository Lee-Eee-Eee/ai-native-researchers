# 科研项目目录与接手方法

先选一条已知的结论，确认能从项目首页找到证据页、结果表、运行命令和输入版本。目录的职责由这条路径决定。新项目可用下面的起点，已有项目在首页注明各目录的对应关系。

## 目录从哪里起步

下面是仓库合成示例已用的目录。小项目从一个入口、一个输入和一套可复算结果开始。

```text
project/
├── README.md                       项目入口、当前问题、运行方法
├── docs/
│   ├── 001_observed-peaks.md        阶段判断
│   ├── 001a_observed-peaks.md       逐例证据与复算命令
│   └── 001_observed-peaks.evidence.json
├── data/observations.csv            示例的合成输入
├── Snakefile                       工作流入口
├── scripts/                        数据检查与汇总
└── results/                        生成的检查报告、处理表和汇总表
```

流程扩大后，按实际用途扩展。项目首页仍指向同号判断与证据、目前的运行入口和最近的已验证产物。

| 要收纳的东西 | 推荐位置与做法 |
| --- | --- |
| 原始输入和来源 | `data/raw/` 可存允许随项目保存的小型原始数据。数据在仪器服务器、机构档案或受限存储时，用 `data/README.md` 或项目已有清单注明位置、标识、版本、获取方式、字段和单位，可用时登记指纹。 |
| 分析脚本、配置和环境 | 从 `scripts/` 起步。Snakemake 多规则项目可用 `workflow/Snakefile`、`workflow/rules/`、`workflow/scripts/`，把选样、时间窗口和参数放进 `config/`。已有可导入包可沿用 `src/`。版本和锁文件随项目记录，虚拟环境、缓存和临时日志在本机重建。 |
| 派生数据、逐例表和科研图 | 默认在 `results/` 按研究阶段或运行号分开，必要时细分 `derived/`、`tables/`、`figures/`。团队原有 `data/processed/` 或 `figures/` 也可沿用。让目录或索引能查回生成这些文件的命令和输入。 |
| 研究记录和文献 | `docs/` 或现有笔记目录存方案、阶段判断与证据，保留唯一可编辑原稿。论文条目按用途放 Zotero 分类，笔记引用具体章节、图或表。稿件使用的 `.bib` 随稿源保留。 |
| 论文、报告和演示 | 项目需要时用 `manuscript/`、`talks/` 或已有交付目录。记录哪份源文件可编辑，以及定稿用的图、表、书目与实验版本。中间稿和已交付版各有明确入口，通过版本记录回看。 |

## 给人和助手的约定

1. **保留原始输入。** 采集文件和参考数据原件供读取。清洗、标定、筛选和模拟输出写到另一位置。更换标定或输入版本后，用新运行号或归档标识留出可追溯的一版。会同时复核的结果各自保有文件和配置。
2. **从项目根目录能复算。** 首页写明运行位置、环境与一条代表性命令。项目内链接用相对路径，数据在外部时给稳定标识和访问办法。新建证据清单会检查同一阶段的输入与产物是否指向同一路径。派生表在另一阶段充当输入时，在该阶段重新登记其来源。
3. **一处编辑，多处可读。** 阶段页、分析代码和稿件各有一份编辑源。个人主库是审阅入口，发布件和构建件标明来自哪个版本。接手目录时沿用已有路径，先补索引再判断是否需要移动文件。改动目录时一起检查项目首页、脚本、相对链接和现有证据清单。
4. **记录科学比较条件。** 用了哪些样本、剔除了什么、如何计分、比较双方能看到哪些输入，这些条件随结果表和阶段判断保存。证据换了就记录新的阶段，旧判断仍能找到对应证据。

## 接手旧项目

找到项目根目录及实际存放 Markdown 的目录。确认旧首页、阶段原稿、结果表、已交付文件和运行入口。让下面的迁移命令先预览索引范围，再生成或刷新 `init.md`。将命令中的 `/path/to/scripts/` 换成技能的实际路径。

```sh
python /path/to/scripts/migrate_project.py --root . --notes docs --dry-run
python /path/to/scripts/migrate_project.py --root . --notes docs
```

如果项目已经把记录放在 `notes/进展`，传 `--notes notes/进展`，索引就写到该目录。命令从原有笔记提取标题和路径，将编号判断与同号证据并列，其余 Markdown 按目录列出。它只写 `init.md` 的自动索引区，保留已有的手写段落。用 Markdown 打开索引，在自动区外补写**目前的研究问题、已确认的判断、还在推进的工作与下一次复算命令**，各项链接回相应原稿。确认入口后，可从原首页或 [Obsidian 主库](review-vault.md)链接这个索引。

后续收尾仍可用 `close_stage.py --notes docs --index README.md`，让它在项目首页追加新阶段。在原首页给 `docs/init.md` 留入口，可用迁移命令随时刷新全量索引。`--notes` 与 `--index` 都指向项目根目录内的路径。跨库的笔记用原库链接或经过验证的审阅入口，接入前先确定谁写原稿。

## 交接前怎么审查

- **走通一个结论。** 从首页或 `init.md` 打开阶段判断、证据页以及结果表，确认引用的是同一批数据。对照表和当前稿件核对一项数字与单位。
- **跑通一个最小结果。** 按记录的环境和根目录运行，核对输出路径和实际内容。已有证据指纹可用 `evidence.py verify` 检查。换一个输入时，只观察需要重算的步骤。 [复算与交接](reproduction.md)
- **检查一次迁移。** 核对索引里一对有编号的笔记和一份普通 Markdown，顺着链接找到原稿。刷新索引前后比对旧笔记及手写内容。阶段记录较多时核对缺少配套页的条目，再决定哪些需补。

## 参考的公开实践

- Wilson 等建议在同一个项目目录内区分文档、源代码、数据和生成结果。The Turing Way 强调研究复现包中的数据、方法、输出与环境必须可辨认，并给出项目说明与版本控制的安排。 [Good enough practices in scientific computing](https://doi.org/10.1371/journal.pcbi.1005510) · [The Turing Way Research Compendia](https://book.the-turing-way.org/reproducible-research/compendia/)
- Project TIER 给计算研究提供输入、分析数据、脚本、结果和报告的完整组织示例，可按项目复杂度调整。Snakemake 为工作流仓库给出 `workflow/`、`config/`、`resources/` 和 `results/` 的具体约定，适合项目已有多步依赖时采用。 [TIER Protocol 4.0](https://www.projecttier.org/tier-protocol/protocol-4-0/) · [Snakemake Distribution and Reproducibility](https://snakemake.readthedocs.io/en/stable/snakefiles/deployment.html)
