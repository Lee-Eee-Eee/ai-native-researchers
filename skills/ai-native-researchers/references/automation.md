# 一条命令收尾一轮实验

算完结果后，让助手读本次命令、输入文件和结果表，填一份小 JSON。研究者审阅其中的 `finding` 和 `next`。脚本把这段判断、文件链接和指纹写入项目，省去逐个建页、编号和补首页链接的工作。脚本只记录 `command` 的原文。

下面用一份温度实验的示例说明格式。正式收尾时把数值、对照和文件名换成这次实验的实际记录。

```json
{
  "id": "thermometer-offset",
  "project": "温度计标定",
  "date": "2026-01-15",
  "question": "校正零点后，第二天的读数准了多少？",
  "finding": "第二天独立记录的 24 个整点里，平均绝对误差从 0.8 °C 降到 0.3 °C。",
  "comparison": "两组使用同一支参考温度计和同一批 24 个整点。零点偏差只用第一天估计。",
  "command": "python analysis/score.py --input data/holdout.csv --out results/score.csv",
  "inputs": ["data/holdout.csv", "analysis/score.py"],
  "outputs": ["results/score.csv"],
  "next": "查看误差最大的两个整点是否都落在快速升温时段。"
}
```

将描述保存为 `stage.json`。下面两条命令在项目根目录运行，将脚本路径换成技能实际安装的位置。默认读取已有的 `README.md`，从 `docs/` 里的最大编号往后排。已有其他目录约定时，补上 `--notes notes/进展 --index 首页.md`。描述里也可给出整数 `number` 来指定编号。

```sh
python /path/to/scripts/close_stage.py stage.json --dry-run
python /path/to/scripts/close_stage.py stage.json
```

预览会检查文件是否齐全并列出将要写入的路径。新建的两页带有 `project`、`stage`、`date` 和 `kind` 属性。`project` 和 `date` 可省略，分别取项目根目录名和首次写入当天。多人共享或迁移路径的项目可显式填写一贯使用的项目名。已有页面会保留原内容和属性。[在主库汇总阶段](review-vault.md#用笔记属性汇总阶段)

正式执行后，从首页点进编号结论页，再点“逐项证据与复算”，即可找到原始结果、计算命令和同号 `.evidence.json`。例如阶段号是 017 时，可在项目根目录单独复核文件内容。

```sh
python /path/to/scripts/evidence.py verify --root . --manifest docs/017_thermometer-offset.evidence.json
```

需要记文献时，在 JSON 中加入 `literature` 列表。每项填 `title`，可加裸 DOI 字段 `doi` 和从 Zotero 实际复制的条目链接 `zotero`。例如 `zotero://select/library/items/ABCD2345` 展示的是格式，个人库和群组库都可使用。

同一份描述可再次执行。脚本会重新核对文件指纹，保留两页上的手写批注和首页内容。指纹改变、编号碰撞或同一 `id` 对应了另一份描述时，命令会报告具体原因。若实验有了新结果，使用新的 `id` 记录下一阶段。若进程意外中止留下项目根目录的 `.ai-native-stage.lock`，先核对其中的进程号和本次文件是否齐全，确认收尾进程已退出后再清除遗留的锁。
