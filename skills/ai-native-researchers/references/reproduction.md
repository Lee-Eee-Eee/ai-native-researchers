# 复算与交接

新项目或接手已有项目时，先用[科研项目目录与接手方法](project-structure.md)核对输入、派生文件、笔记、代码和交付物的位置。

从一个交付结果向前追。例如逐例评分表依赖两组预测和一份样本划分，预测又依赖模型版本、预处理和参数。列出这些关系，再写规则。把会影响结果的外部文件声明为输入，计算配置作为输入或规则参数。记录随机种子、环境版本和代码提交。数据不能公开时，给出获取方式、版本、文件格式和能公开的小样例。

先做 dry run 看依赖和规模，再在小数据上实际运行。检查输出内容。第二次运行应识别已有且有效的结果。改动一个输入后检查哪些规则该重跑。长作业先检查现有进程、调度记录和输出，避免重复提交。碰到部分失败，检查日志和已有产物，按工作流支持的恢复方式重试。

## 给结果表留一份指纹

使用随技能提供的 `scripts/evidence.py`。在项目目录运行，下面的脚本路径按实际安装位置填写。

```sh
python /path/to/evidence.py record --root . --manifest evidence/run-017.json --input data/observations.csv --output results/summary.csv
python /path/to/evidence.py verify --root . --manifest evidence/run-017.json
```

可多次传入 `--input` 和 `--output`，包括脚本与配置。它逐文件计算 SHA-256，并在可用时记录当时的 Git 提交及工作区状态。它校验文件内容；哪条命令生成了它、采用了什么划分、能否在另一台机器重算，要在证据页记录并实测。清单只收项目根目录内的文件，路径相对该目录，便于迁移。外置归档数据可以另记其仓储标识或校验值。

[Snakemake 官方教程](https://snakemake.readthedocs.io/en/stable/tutorial/basics.html)
