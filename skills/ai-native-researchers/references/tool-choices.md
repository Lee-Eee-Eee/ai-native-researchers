# 随研究的实际需要选择工具

先看项目已经使用的环境。早期项目用 Git、Markdown 和一个可运行脚本就能开始。整理流程时，问最近一轮哪里在反复修表、换算、跑代码、找原图或核对引用。从一个实际产物试接，检查接入后省掉了哪项重复操作，以及同事能否沿着原有入口复查。

| 何时值得加工具 | 优先考虑 | 接入后检验什么 |
| --- | --- | --- |
| 相关论文越来越多，反复手抄题录 | [Crossref REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) 核对 DOI 元数据，用 [OpenAlex](https://docs.openalex.org/) 追溯引文，导入 Zotero | 检查 DOI、期刊版和预印本关系；抽一篇从研究判断回到原文图表 |
| 提交前要复核核心论据所引的论文 | 用 [Crossref Retraction Watch](https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/) 辅助查撤稿，打开出版社页面核对更正与版本 | 记核对日期及公告出处，判断被更新的内容是否影响稿中引用的结论 |
| 多人共用仪器，样本和标定容易串号 | 沿用实验室 ELN 或 [eLabFTW](https://www.elabftw.net/)，给样本、标准品、校准和原始文件分配可交叉检索的编号 | 从一行处理结果倒查样本、仪器设置、操作者和当天的校准 |
| PDF 批注和研究笔记落在两个地方 | [ZotLit](https://zotlit.aidenlx.site/docs/install-zotlit) 对接 Obsidian 与 Zotero；写稿继续用项目的 BibTeX 或 CSL JSON | 用真实条目更新一遍笔记，核对手写段落与页码链接 |
| 阶段笔记散在多个项目，需要在主库一起查看 | 用 Obsidian Bases 根据笔记属性显示[科研阶段视图](review-vault.md#用笔记属性汇总阶段) | 打开不同项目的同号记录，检查判断和证据是否归入正确项目，原稿路径是否正确 |
| 数据变动后，脚本还能跑，但单位或分组错了 | 先写少量断言；跨团队交换表格时可发 [Table Schema](https://specs.frictionlessdata.io/table-schema/) | 故意放入一条重复键、非法单位或缺值，确认在正确的一步被检出 |
| 多台仪器的时钟、坐标或观测窗口需要逐次对照 | 用 [Astropy Time](https://docs.astropy.org/en/stable/time/) 换算天文时标，用 [xarray](https://docs.xarray.dev/en/stable/generated/xarray.align.html) 管有名字的坐标轴，先定匹配窗口和覆盖条件 | 记录原始时标，用已知时刻核对转换结果。为预期相同的索引用 `join="exact"`，用一条错位记录检查能否检出 |
| 组员反复从导出的表格里手动修列、日期或分类名 | 用 [OpenRefine](https://openrefine.org/docs/manual/running/) 导出可重放的清洗操作，保留原表与人工修订记录 | 在新导出的一批表上重放，抽查行数和几处典型变化，单元格的单次人工修改另记 |
| 原始数据或权重过大，无法用普通 Git 分享 | [DVC](https://doc.dvc.org/start) 跟踪大文件指针和内容版本。已有机构档案库时也可保存仓储 ID、版本和 SHA-256 | 在另一份检出中取回同版本小样，核对指纹。外部存储权限单独核对 |
| 同事装出的软件版本不一致 | Python 用 [uv 锁文件](https://docs.astral.sh/uv/concepts/projects/sync/)，R 用 [renv](https://rstudio.github.io/renv/)，有系统依赖或集群任务时考虑 [Apptainer](https://apptainer.org/docs/user/latest/) 镜像及摘要 | 从新环境重跑小样。涉及 GPU 时同时记驱动、硬件与数值容差 |
| Notebook 只在当前会话能跑，或 `.ipynb` 的变更难审阅 | 用 [nbclient](https://nbclient.readthedocs.io/en/latest/client.html) 从干净内核重跑，需要在 Git 审阅代码时再用 [Jupytext](https://jupytext.org/using/paired-notebooks/) 配对文本 | 在指定环境执行并核对关键输出。计算步骤稳定后可接进现有 Snakemake |
| 一张表要串起多个脚本 | [Snakemake](https://snakemake.readthedocs.io/en/stable/tutorial/basics.html) 管输入输出；已有稳定工作流时沿用其规则 | 改一个输入，看受影响的规则是否重跑。执行、结果内容、重复运行分别核对 |
| 需要排队运行很多组工况 | [Slurm](https://slurm.schedmd.com/quickstart.html) 作业、数组或 Snakemake 执行器，保存调度 ID 和资源上限 | 用现有作业 ID 查队列和完成状态，按失败组恢复；确认输出能对应原参数 |
| 多组并行，一人修改标定后不知该通知谁 | 用团队现有 issue 板或 [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects) 记负责人、依赖、产物和等待的决定 | 抽查一个上游变更，找出哪些计算、图和结论需要复核 |
| 上百次训练让人分不清哪个模型出了哪张图 | [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) 记 run、参数、指标、模型路径；十来组普通实验用 CSV 就够 | 用 run ID 找回划分、种子、模型和逐例输出，再独立算一次指标 |
| 得到很多结果，想确认最初的判断还成立 | [OSF 注册](https://www.cos.io/initiatives/prereg) 或团队内部带日期的方案，记录主要终点、划分与停止条件 | 读者能区分预先计划和事后探索，能指出验证用到哪个独立批次 |
| 报告图和数字经常晚于代码 | 从结果表出图，用 [Quarto](https://quarto.org/docs/computations/) 或项目现有 LaTeX 构建。汇报、论文和文风调整见[交付流程](research-outputs.md) | 从干净目录构建，逐项比对一幅图、一个正文数字和一条引文 |
| 有人要引用某一版软件或复用整套成果 | [CITATION.cff](https://citation-file-format.github.io/) 写引用信息；用 [Zenodo](https://help.zenodo.org/docs/github/) 归档已批准的发布版本；需跨机构交换时考虑 [RO-Crate](https://www.researchobject.org/ro-crate/) | 检查元数据中的作者、许可证、版本 DOI 和文件范围，保留受限数据的获取办法 |
| 大批文件跨机构移交，接收方要求标准校验清单 | 按接收方约定用 [BagIt](https://datatracker.ietf.org/doc/html/rfc8493) 封装载荷和指纹，沿用项目现有证据清单记录来源 | 在接收端核对清单及内容，确认损坏或缺失的文件可定位 |
| 工作站损坏会丢失原始数据或实验笔记 | 沿用机构备份策略；需要加密的增量备份时可用 [restic](https://restic.readthedocs.io/en/stable/) | 在独立位置恢复一小组样本，并与登记的指纹比对，记录恢复日期 |

一次只接入当前需要的环节。例如只有一张预测表需要更新时，直接运行目标规则。要交接整个论文项目时，再从图表一路检查到样本、书目、环境、工作流和发布记录。
