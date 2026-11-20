# 随研究的实际需要选择工具

先看项目已经使用的环境。早期项目用 Git、Markdown、一个可运行脚本就能开始。下表按遇到的问题选工具，每引入一种，都应能指认它减少了哪项手工操作，以及怎样验证。

| 何时值得加工具 | 优先考虑 | 接入后检验什么 |
| --- | --- | --- |
| 相关论文越来越多，反复手抄题录 | [Crossref REST](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) 核对 DOI 元数据，用 [OpenAlex](https://docs.openalex.org/) 追溯引文，导入 Zotero | 检查 DOI、期刊版和预印本关系；抽一篇从研究判断回到原文图表 |
| 多人共用仪器，样本和标定容易串号 | 沿用实验室 ELN 或 [eLabFTW](https://www.elabftw.net/)，给样本、标准品、校准和原始文件分配可交叉检索的编号 | 从一行处理结果倒查样本、仪器设置、操作者和当天的校准 |
| PDF 批注和研究笔记落在两个地方 | [ZotLit](https://zotlit.aidenlx.site/docs/install-zotlit) 对接 Obsidian 与 Zotero；写稿继续用项目的 BibTeX 或 CSL JSON | 用真实条目更新一遍笔记，核对手写段落与页码链接 |
| 数据变动后，脚本还能跑，但单位或分组错了 | 先写少量断言；跨团队交换表格时可发 [Table Schema](https://specs.frictionlessdata.io/table-schema/) | 故意放入一条重复键、非法单位或缺值，确认在正确的一步被检出 |
| 原始数据或权重过大，无法用普通 Git 分享 | [DVC](https://doc.dvc.org/start) 跟踪大文件指针和内容版本。已有机构档案库时也可保存仓储 ID、版本和 SHA-256 | 在另一份检出中取回同版本小样，核对指纹。外部存储权限单独核对 |
| 同事装出的软件版本不一致 | Python 用 [uv 锁文件](https://docs.astral.sh/uv/concepts/projects/sync/)，R 用 [renv](https://rstudio.github.io/renv/)，有系统依赖或集群任务时考虑 [Apptainer](https://apptainer.org/docs/user/latest/) 镜像及摘要 | 从新环境重跑小样。涉及 GPU 时同时记驱动、硬件与数值容差 |
| 一张表要串起多个脚本 | [Snakemake](https://snakemake.readthedocs.io/en/stable/tutorial/basics.html) 管输入输出；已有稳定工作流时沿用其规则 | 改一个输入，看受影响的规则是否重跑。执行、结果内容、重复运行分别核对 |
| 需要排队运行很多组工况 | [Slurm](https://slurm.schedmd.com/quickstart.html) 作业、数组或 Snakemake 执行器，保存调度 ID 和资源上限 | 用现有作业 ID 查队列和完成状态，按失败组恢复；确认输出能对应原参数 |
| 多组并行，一人修改标定后不知该通知谁 | 用团队现有 issue 板或 [GitHub Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects) 记负责人、依赖、产物和等待的决定 | 抽查一个上游变更，找出哪些计算、图和结论需要复核 |
| 上百次训练让人分不清哪个模型出了哪张图 | [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/) 记 run、参数、指标、模型路径；十来组普通实验用 CSV 就够 | 用 run ID 找回划分、种子、模型和逐例输出，再独立算一次指标 |
| 得到很多结果，想确认最初的判断还成立 | [OSF 注册](https://www.cos.io/initiatives/prereg) 或团队内部带日期的方案，记录主要终点、划分与停止条件 | 读者能区分预先计划和事后探索，能指出验证用到哪个独立批次 |
| 报告图和数字经常晚于代码 | 用 [Quarto](https://quarto.org/docs/computations/) 或项目现有 LaTeX 构建，从结果表产生图表；用 CI 在合成样本上回归 | 从干净目录构建，逐项比对一幅图、一个正文数字和一条引文 |
| 有人要引用某一版软件或复用整套成果 | [CITATION.cff](https://citation-file-format.github.io/) 写引用信息；用 [Zenodo](https://help.zenodo.org/docs/github/) 归档已批准的发布版本；需跨机构交换时考虑 [RO-Crate](https://www.researchobject.org/ro-crate/) | 检查元数据中的作者、许可证、版本 DOI 和文件范围，保留受限数据的获取办法 |
| 工作站损坏会丢失原始数据或实验笔记 | 沿用机构备份策略；需要加密的增量备份时可用 [restic](https://restic.readthedocs.io/en/stable/) | 在独立位置恢复一小组样本，并与登记的指纹比对，记录恢复日期 |

一次只接入当前需要的环节。例如只有一张预测表需要更新时，直接运行目标规则。要交接整个论文项目时，再从图表一路检查到样本、书目、环境、工作流和发布记录。
