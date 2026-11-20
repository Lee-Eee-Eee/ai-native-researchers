# 从论文走到研究判断

1. 确定目标库和项目分类。按 DOI 比对已有条目，缺少 DOI 时用题名、第一作者、年份一起核对。遇到预印本、期刊版或同名方法，分清版本。已有条目可加入多个分类，并保留笔记和附件。
2. 项目编号页保留论文 DOI 或正式出版页，以及指向本机 Zotero 条目的链接。个人库条目使用 `zotero://select/library/items/<itemKey>`，群组库使用 `zotero://select/groups/<groupID>/items/<itemKey>`。分类将 `items` 换成 `collections`。先从库中读回 key。论文的 BibTeX 引文键由书目文件管理。
3. 为直接相关的论文写一句可核查的依据，例如“图 3 在固定采样间隔下比较四种办法”。标明实际读到的段落、图或表。项目里的实验结论另附自己的结果文件。
4. 用 ZotLit 时核对 Obsidian 桌面安装器、应用版本、插件版本及 Zotero 版本。先选一个已有条目，指定库内文献笔记目录，生成一篇笔记并核对题名、条目和引用跳转。有附件或批注时再检验导入，更新一次，确认手写段落仍在。只有导出文件或插件已下载时，据实记录所到环节。
5. 优先使用官方本地接口和已有连接。Zotero 10 的本地 API 读写权限不同。需要写入时使用正式授权，读回目标分类及条目复核。公开交付示例时使用合成记录或公开书目信息，项目自己的文库、批注、PDF 与授权信息保留在本地。

### 在后台生成单篇阅读页

Zotero 已开启本地 API 时，可以直接读取条目，生成一篇含作者、DOI 和 PDF 跳转的笔记。把命令中的示例键换成真实的 8 位条目键。可再传 `--group` 和数字群组 ID。

```sh
python /path/to/scripts/zotero_note.py ABCD2345 --counts --out "papers/reading.md"
```

脚本只替换自己标记的书目区，保留下方的阅读判断。批注数用于判断有没有材料可读。需要把划线原文与页码导入 Obsidian 时，使用 ZotLit 的批注导入。

[Zotero 本地 API](https://www.zotero.org/support/dev/web_api/v3/local_api) · [分类](https://www.zotero.org/support/collections_and_tags) · [ZotLit 安装](https://zotlit.aidenlx.site/docs/install-zotlit) · [Obsidian 跨库链接](https://help.obsidian.md/Extending+Obsidian/Obsidian+URI)
