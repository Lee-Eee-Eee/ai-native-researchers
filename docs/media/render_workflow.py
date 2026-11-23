"""Draw the bilingual README overview and an optional portrait cover with ohmyplt."""

from argparse import ArgumentParser
from io import BytesIO
import os
from pathlib import Path
import sys

import matplotlib
from PIL import Image
from resvg_py import svg_to_bytes

matplotlib.use("Agg")
from matplotlib import pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import Circle


HERE = Path(__file__).resolve().parent
WINDOWS_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
DPI = 152.4
MM_PER_PIXEL = 1 / 6
PT_PER_PIXEL = 72 / DPI
PAPER = "#F8F6F0"
INK = "#192922"
GREEN = "#25634C"
MUTED = "#4E5F55"
LINE = "#BDCCC1"
CANVAS = "#FFFEFA"
MINT = "#ECF2EB"
RUST = "#A2422E"

BRAND = "ai-native-researchers.png"
ASSETS = {
    "Zotero": "zotero.png",
    "Obsidian": "obsidian.svg",
    "Git": "git.svg",
    "Snakemake": "snakemake.svg",
    "ohmyplt": "ohmyplt.png",
}
STAGES = (
    ("Zotero", "Obsidian"),
    ("Git", "Snakemake"),
    ("ohmyplt", "PowerPoint / Beamer", "LaTeX"),
)
COPY = {
    "zh": {
        "stage": ("文献与研究记录", "代码与数据分析", "图表、汇报与论文"),
        "roles": ("文献条目与批注", "阶段记录与审阅", "代码和配置的版本",
                  "分析步骤与依赖", "科研绘图", "组会与学术汇报", "图表与书目"),
        "overview": "AI 参与的科研工作流",
    },
    "en": {
        "stage": ("Papers & notes", "Code & analysis", "Research outputs"),
        "roles": ("Papers and annotations", "Milestone notes and review",
                  "Code and config versions", "Rules and dependencies", "Scientific figures",
                  "Lab meetings and talks", "Figures and bibliography"),
        "overview": "A research workflow for the AI era",
    },
}


def get_font(role):
    filenames, families, weight = {
        "zh": ("msyh.ttc", ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC"), "normal"),
        "zh-bold": ("msyhbd.ttc", ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC"), "bold"),
        "serif": ("NotoSerifSC-VF.ttf", ("Noto Serif CJK SC", "Noto Serif SC", "Songti SC"), "normal"),
        "latin": ("arial.ttf", ("Arial", "Liberation Sans", "DejaVu Sans"), "normal"),
        "latin-bold": ("arialbd.ttf", ("Arial", "Liberation Sans", "DejaVu Sans"), "bold"),
        "mono": ("consola.ttf", ("Consolas", "Liberation Mono", "DejaVu Sans Mono"), "normal"),
    }[role]
    path = WINDOWS_FONTS / filenames
    if path.is_file():
        return FontProperties(fname=path)
    for family in families:
        properties = FontProperties(family=family, weight=weight)
        try:
            findfont(properties, fallback_to_default=False)
        except ValueError:
            continue
        return properties
    if role == "serif":
        return get_font("zh-bold")
    raise RuntimeError(f"Install one of these fonts: {', '.join(families)}")


def load_icons():
    icons = {}
    for key, filename in [("brand", BRAND), *ASSETS.items()]:
        path = HERE / "tools" / filename
        if path.suffix == ".svg":
            source = path.read_text(encoding="utf-8")
            if key == "Obsidian":
                source = source.replace('height="100%" width="100%"',
                                        'height="512" width="512"', 1)
            path = BytesIO(svg_to_bytes(svg_string=source, width=256, dpi=96))
        with Image.open(path) as image:
            icons[key] = image.convert("RGBA")
    return icons


class Diagram:
    """Lay out labels, icons and ports in pixels on an ohmyplt Plate."""

    def __init__(self, plate, icons, fonts, width, height, language):
        self.icons, self.fonts = icons, fonts
        self.width, self.height = width, height
        self.normal = "zh" if language == "zh" else "latin"
        self.bold = f"{self.normal}-bold"
        self.copy = COPY[language]
        self.plate = plate(width * MM_PER_PIXEL, height * MM_PER_PIXEL)
        self.fig, self.ax = self.plate.fig, self.plate.ax
        self.fig.set_facecolor(PAPER)
        self.roles = dict(zip(sum(STAGES, ()), self.copy["roles"], strict=True))

    def xy(self, x, y):
        return x * MM_PER_PIXEL, (self.height - y) * MM_PER_PIXEL

    def text(self, x, y, value, size, *, face=None, color=INK, align="left"):
        self.plate.text(
            *self.xy(x, y), value, size=size * PT_PER_PIXEL,
            fontproperties=self.fonts[face or self.normal], color=color,
            ha=align, va="center",
        )

    def wire(self, *points, color=GREEN, width=2, arrow=True, radius=14):
        self.plate.wire(
            [self.xy(*point) for point in points], color=color, lw=width * PT_PER_PIXEL,
            r=radius * MM_PER_PIXEL, arrow=arrow, head=15 * PT_PER_PIXEL,
        )

    def rule(self, x, y, end):
        self.wire((x, y), (end, y), color=LINE, width=1.25, arrow=False)

    def port(self, x, y):
        self.ax.add_patch(Circle(self.xy(x, y), 4 * MM_PER_PIXEL, facecolor=PAPER,
                                 edgecolor=GREEN, lw=1.6 * PT_PER_PIXEL, zorder=4))

    def box(self, x, y, w, h, *, face=CANVAS):
        self.plate.card(*self.xy(x, y + h), w * MM_PER_PIXEL, h * MM_PER_PIXEL,
                        face=face, edge=LINE, lw=1.4 * PT_PER_PIXEL, r=20 * MM_PER_PIXEL)

    def picture(self, key, x, y, size):
        image = self.icons[key]
        scale = size / max(image.size)
        w, h = (value * scale for value in image.size)
        left, bottom = self.xy(x - w / 2, y + h / 2)
        right, top = self.xy(x + w / 2, y - h / 2)
        self.ax.imshow(image, extent=(left, right, bottom, top), aspect="auto",
                       interpolation="lanczos", zorder=5)

    def tool_mark(self, tool, x, y, size):
        if tool in self.icons:
            self.picture(tool, x, y, size)
            return
        # Pictograms for the output formats.
        s = size * .44
        if tool == "PowerPoint / Beamer":
            self.wire((x - s, y + .40 * s), (x - s, y - .78 * s),
                      (x + s, y - .78 * s), (x + s, y + .40 * s), (x - s, y + .40 * s),
                      color=RUST, radius=2, arrow=False, width=2.5)
            self.wire((x, y + .40 * s), (x, y + .86 * s),
                      color=RUST, arrow=False, width=2.5)
            self.wire((x - .44 * s, y + .86 * s), (x + .44 * s, y + .86 * s),
                      color=RUST, arrow=False, width=2.5)
            self.wire((x - .58 * s, y + .03 * s), (x - .15 * s, y - .30 * s),
                      (x + .18 * s, y - .12 * s), (x + .54 * s, y - .47 * s),
                      color=RUST, arrow=False, width=2)
        else:
            self.wire((x - .60 * s, y - .92 * s), (x + .20 * s, y - .92 * s),
                      (x + .70 * s, y - .41 * s), (x + .70 * s, y + .90 * s),
                      (x - .60 * s, y + .90 * s), (x - .60 * s, y - .92 * s),
                      arrow=False, radius=2, width=2.5)
            for offset in (-.18, .18, .54):
                self.wire((x - .27 * s, y + offset * s), (x + .41 * s, y + offset * s),
                          arrow=False, width=2)

    def tool(self, name, x, y, *, size=34, detail=25, icon=48):
        self.tool_mark(name, x + icon / 2, y, icon)
        self.text(x + icon + 18, y - 15, name, size, face="latin-bold")
        self.text(x + icon + 18, y + 22, self.roles[name], detail, color=MUTED)

    def analysis_path(self, x, y, width, size):
        center = x + width / 2
        shift = width * .35
        self.text(center - shift, y, "data/", size, face="mono", color=GREEN, align="center")
        step = "分析规则" if self.normal == "zh" else "Rules"
        self.text(center, y, step, size, face=self.bold, color=GREEN, align="center")
        self.text(center + shift, y, "results/", size, face="mono", color=GREEN, align="center")
        for sign in (-1, 1):
            midpoint = center + sign * shift / 2
            half = min(width * .034, 15)
            self.wire((midpoint - half, y), (midpoint + half, y), width=1.7)

    def save(self, destination):
        self.fig.set_dpi(DPI)
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()
        for label in self.ax.texts:
            box = label.get_window_extent(renderer)
            if not (0 < box.x0 and box.x1 < self.width and 0 < box.y0 and box.y1 < self.height):
                raise ValueError(f"Label outside the diagram: {label.get_text()}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        with BytesIO() as buffer:
            self.fig.savefig(buffer, format="png", dpi=DPI, facecolor=PAPER)
            buffer.seek(0)
            with Image.open(buffer) as image:
                if image.size != (self.width, self.height):
                    raise ValueError(f"Unexpected canvas: {image.size}")
                image.convert("RGB").save(destination, optimize=True)
        plt.close(self.fig)


def portrait(diagram):
    diagram.picture("brand", 101, 98, 56)
    diagram.text(146, 99, "AI-Native Researchers", 36, face="latin-bold")
    diagram.text(69, 204, "“模型一代”科研范式", 90, face="serif")
    diagram.text(75, 293, "一套便于审阅、协作和迁移的科研工作流", 35, color=MUTED)
    diagram.rule(72, 347, 1008)

    headings = diagram.copy["stage"]
    diagram.text(72, 393, headings[0], 31, face=diagram.bold, color=GREEN)
    for x, name in zip((72, 558), STAGES[0], strict=True):
        diagram.box(x, 433, 450, 116)
        diagram.tool(name, x + 26, 492, size=37, detail=28, icon=54)

    diagram.wire((297, 549), (297, 581), (783, 581), (783, 549), arrow=False)
    diagram.wire((540, 581), (540, 624))
    diagram.port(540, 581)

    diagram.box(72, 629, 936, 301, face=MINT)
    diagram.text(102, 676, headings[1], 32, face=diagram.bold, color=GREEN)
    for x, name in zip((104, 586), STAGES[1], strict=True):
        diagram.tool(name, x, 754, size=37, detail=28, icon=54)
    diagram.rule(102, 809, 978)
    diagram.analysis_path(103, 865, 874, 30)

    output_centers = (230, 540, 850)
    diagram.wire((540, 930), (540, 983), arrow=False)
    for x in output_centers:
        diagram.wire((540, 983), (x, 983), (x, 1042))
    diagram.port(540, 983)

    diagram.box(72, 1048, 936, 310)
    diagram.text(102, 1100, headings[2], 32, face=diagram.bold, color=GREEN)
    for x, name in zip(output_centers, STAGES[2], strict=True):
        diagram.tool_mark(name, x, 1176, 54)
        diagram.text(x, 1241, name, 30, face="latin-bold", align="center")
        diagram.text(x, 1291, diagram.roles[name], 26, color=MUTED, align="center")


def landscape(diagram):
    diagram.text(52, 59, diagram.copy["overview"], 40, face=diagram.bold)
    diagram.rule(52, 102, 1388)
    boxes = ((52, 384), (506, 430), (1006, 382))
    for i, ((x, width), caption) in enumerate(zip(boxes, diagram.copy["stage"], strict=True)):
        diagram.box(x, 138, width, 340, face=MINT if i == 1 else CANVAS)
        diagram.text(x + 25, 179, caption, 29, face=diagram.bold, color=GREEN)
        if i < 2:
            diagram.port(x + width, 306)
            diagram.wire((x + width + 5, 306), (boxes[i + 1][0] - 8, 306))
    for index, names in enumerate(STAGES):
        x, width = boxes[index]
        for row, name in enumerate(names):
            diagram.tool(name, x + 26, (241 if index == 2 else 252) + row * (86 if index == 2 else 89),
                         size=26, detail=23, icon=44)
        if index == 1:
            diagram.rule(x + 25, 393, x + width - 25)
            diagram.analysis_path(x + 14, 437, width - 28, 21)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--ohmyplt", type=Path, default=Path.home() / ".codex" / "skills" / "ohmyplt",
                        help="Path to the ohmyplt skill directory")
    parser.add_argument("--cover", type=Path, help="Render the matching 1080 × 1440 cover to this PNG")
    args = parser.parse_args()
    scripts = args.ohmyplt / "scripts"
    if not (scripts / "ohmyplt.py").is_file():
        parser.error("Install ohmyplt or pass its skill directory with --ohmyplt.")
    sys.path.insert(0, str(scripts.resolve()))
    from ohmyplt import Plate, configure

    fonts = {role: get_font(role) for role in ("zh", "zh-bold", "serif", "latin", "latin-bold", "mono")}
    configure(body_font=fonts["latin"].get_name(), fallback_fonts=(fonts["zh"].get_name(),))
    icons = load_icons()
    for language, suffix in (("zh", ""), ("en", ".en")):
        panel = Diagram(Plate, icons, fonts, 1440, 520, language)
        landscape(panel)
        panel.save(HERE / f"research-workflow{suffix}.png")
    if args.cover:
        panel = Diagram(Plate, icons, fonts, 1080, 1440, "zh")
        portrait(panel)
        panel.save(args.cover)


if __name__ == "__main__":
    main()
