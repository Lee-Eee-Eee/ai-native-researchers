# AI-Native Researchers

[简体中文](README.md) · [Example project](#example-project) · [Install](#install)

I've been learning to do research and to work with AI at the same time. I ask an assistant to find papers and run analyses, then go back through the chat to find a source for a lab meeting. As the experiments go on, there's more to look up. The code and results are in the project folder. The choices we made about the comparisons and the reasons for changing a parameter are in the conversations. When I start a fresh chat or hand the project to a colleague, I have to explain it all over again.

I wanted to open one project page and find the papers I had read, a record of each round, and the drafts and reports we had sent out. I could see where things stood and change the plan when it was time to try a different comparison or investigate an unusual result. A colleague could pick up the work from the same page. I turned that workflow into **AI-Native Researchers**, an installable skill for managing research projects. [Roles of researchers and assistants](skills/ai-native-researchers/references/model-generation.md)

The name comes from two essays. Jiang Yifan writes about students and early-career researchers reconsidering their choices as AI arrives. Deng Geng takes up the same discussion and writes about deciding for ourselves what is worth doing. [Jiang Yifan's 《模型一代》](https://mp.weixin.qq.com/s?__biz=MzY5MzQ5NjgwNw==&mid=2247483674&idx=1&sn=facf9067217689d466efddf475190a59&chksm=f58d87e227d875dd4dbccbe0f66cb383fddcdcec95ac66a3f992d1cc87dcad1e71f021ad9d61#rd) · [Deng Geng's 《模型万代》](https://mp.weixin.qq.com/s?__biz=MzI0NjY1MDIwMQ==&mid=2247484921&idx=1&sn=ada6ae5a6af92849c49470672d803534&chksm=e8c21d1f61e9b6ccd0641eba378278df7a9cea53d2224a8ab931699635458abda2a5d1392afa#rd)

![The project home sits between Obsidian and Zotero on the left and Git and Snakemake on the right, with ohmyplt figures, PowerPoint presentations, and LaTeX papers below.](docs/media/research-workflow.en.png)

## The research workflow

### <img src="docs/media/tools/zotero.png" width="22" height="22" alt=""> Papers and reading notes

After a search, I add the papers I've checked to the project's Zotero collection. In the milestone note, I link the papers I actually used and jot down the relevant section or figure number. The next time I need that figure, I can go straight from the note to the paper. I can also sync the collection's bibliography and reading notes to Obsidian. [Library sync](skills/ai-native-researchers/references/library-sync.md) · [ZotLit annotations](skills/ai-native-researchers/references/literature.md)

### <img src="docs/media/tools/obsidian.svg" width="22" height="22" alt=""> Experiment notes and next steps

After each round of experiments, I ask the assistant to write two Markdown notes. In `001`, we record what we tried, my assessment of the results, and the next step. The companion note `001a` links to results tables and run records and calls out unusual cases. I review both notes in Obsidian and add comments beside the relevant results. When I open a new conversation, I ask the assistant to read the project home and the notes from the last round. [Review in Obsidian](skills/ai-native-researchers/references/review-vault.md)

### <img src="docs/media/tools/git.svg" width="22" height="22" alt=""> <img src="docs/media/tools/snakemake.svg" width="22" height="22" alt=""> Files, versions, and analysis

I keep raw data, code and configuration, results, and deliverables in separate places. Git tracks the code, configuration, and notes. When data or model weights live elsewhere, I ask the assistant to record their location and version. For a multi-step analysis, I write the inputs and outputs of each step as Snakemake rules. Snakemake can then update the results that depend on a changed input. [Project layout](skills/ai-native-researchers/references/project-structure.md) · [Run records](skills/ai-native-researchers/references/reproduction.md) · [Snakemake example](skills/ai-native-researchers/assets/snakemake-starter/)

### <img src="docs/media/tools/ohmyplt.svg" width="22" height="22" alt=""> Figures, talks, and papers

For a talk, I pick results from the milestone notes, plot them with ohmyplt, and put the figures in PowerPoint or Beamer. I use the project's LaTeX template and Zotero bibliography for the paper. I link the figures, tables, and both the editable and final files from the milestone note so I can find them again when I revise the work. [ohmyplt](https://github.com/Lee-Eee-Eee/ohmyplt) · [Research outputs](skills/ai-native-researchers/references/research-outputs.md)

## Bringing in an existing project

When I organize an existing project, I start by generating a `docs/init.md` index of the Markdown files already there. I add the index to the project home along with links to the current work, results, and drafts. I use relative paths inside the project, so a colleague who receives the shared folder and data notes can start from the home page. [Project layout and migration](skills/ai-native-researchers/references/project-structure.md)

Teams can use their existing tools for data versioning, cluster scheduling, and archiving. [Tool guide](skills/ai-native-researchers/references/tool-choices.md) · [Icon sources](docs/media/tools/sources.md)

## Example project

I kept the **XeSINE-Net** directory layout and milestones `142` through `156` for this example and wrote demonstration notes for them. Open the project home for the current work, next steps, and literature. Open a milestone such as `142` to find its companion, `142a`. Source code, configuration, results, and deliverables are in `code/`, `configs/`, `results/`, and `output/`, respectively. [Explore the XeSINE-Net project layout](examples/xesine-notes/)

The Zotero screenshot shows the SEP Physics and Transport collection in my library. [Zotero screenshot](examples/xesine-notes/previews/zotero.png)

## Install

Send the following installation request to Codex.

> Install skills/ai-native-researchers from Lee-Eee-Eee/ai-native-researchers.

For a manual install, copy the entire [skills/ai-native-researchers](skills/ai-native-researchers/) directory to `~/.codex/skills/`. After installation, assign a task in a new conversation.

> Use $ai-native-researchers to close out the experiment I just ran. Keep my existing project layout, write a milestone decision, and link the case-level results and the command that builds the table.

[Skill instructions](skills/ai-native-researchers/SKILL.md)
