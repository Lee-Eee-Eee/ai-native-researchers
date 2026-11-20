# 把一个 Zotero 分类接进阅读笔记

在 Obsidian 项目库里选一个目录放文献笔记。先打开 Zotero 桌面端并允许本地应用读取文库。分类链接最后八位是分类键，例如个人库链接 `zotero://select/library/collections/ABCD2345` 对应 `ABCD2345`。每次运行都读取该分类及其所有子分类；一篇论文即使收进多个子分类，也只会生成一份笔记。

在技能源码目录运行以下命令。把示例分类键和引号里的目录换成自己的；相对目录会以当前终端的位置解析。第一次加上 `--dry-run` 预览新建和更新的篇数，去掉该参数后执行。已安装技能也可以直接用其 `scripts/zotero_collection.py` 的绝对路径运行。

```sh
python scripts/zotero_collection.py ABCD2345 --out-dir "/path/to/vault/文献笔记" --index "文献目录.md" --counts --dry-run
python scripts/zotero_collection.py ABCD2345 --out-dir "/path/to/vault/文献笔记" --index "文献目录.md" --counts
```

群组分类可从 `zotero://select/groups/123456/collections/ABCD2345` 读出群组 ID，并在同一命令中加上 `--group 123456`。可省略 `--counts` 来跳过子笔记与 PDF 批注计数。程序通过 Zotero 本地只读 API 工作。

每份新笔记按条目键命名，包含题名、作者、日期和可以直接打开的 Zotero 链接。手写内容放在“我的阅读笔记”下方。在同一输出目录里重命名笔记、移入子目录后，只要保留自动生成区两端的 HTML 注释，下次同步还会找到它。移出 Zotero 分类的旧笔记会留在原处。碰到两个文件认领了同一个条目，或预期文件名已被一篇普通笔记占用时，预览会指出冲突位置。调整文件名或保留一份有效的条目标记后再运行即可。

加上 `--index "文献目录.md"` 会在输出目录里按题名列出可点开的阅读笔记。目录页可以留手写文字，写在自动生成区外即可。如果原来就有同名手写目录，给新目录换一个文件名。

只刷新一本书或一篇论文时，见[从论文走到研究判断](literature.md)。
