"""Render the README panels from the Xiaohongshu cover layout using ohmyplt."""

from argparse import ArgumentParser
from io import BytesIO
import os
from pathlib import Path
import sys

import matplotlib
from PIL import Image
from resvg_py import svg_to_bytes

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import Circle, Rectangle


HERE = Path(__file__).resolve().parent
WINDOWS_FONTS = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
WIDTH, HEIGHT, DPI = 1080, 1440, 152.4
CROP = (0, 422, WIDTH, 1318)
PAPER = "#F7F8F4"
DARK, FILM, LIGHT, MINT = "#142F27", "#1B3C31", "#F0F5ED", "#A3C5B0"
TOOLS = ("obsidian.svg", "zotero.png", "git.svg", "snakemake.svg")
OUTPUTS = ("ohmyplt.png", "slides", "paper")

WORDS = {
    "zh": {
        "headings": ("笔记与文献", "版本与分析"),
        "roles": ("阶段判断与证据", "原文与批注", "代码与参数版本", "数据与运行入口"),
        "home": "项目首页",
        "home_detail": "问题 · 判断 · 下一步",
        "outputs_title": "可编辑成果",
        "outputs": ("论文配图", "学术汇报", "论文排版"),
        "formats": ("ohmyplt", "可编辑 PowerPoint", "LaTeX 源文件"),
    },
    "en": {
        "headings": ("Notes and literature", "Versions and analysis"),
        "roles": ("Decisions and evidence", "Papers and annotations", "Code and config versions", "Inputs and run commands"),
        "home": "Project home",
        "home_detail": "Question · Finding · Next step",
        "outputs_title": "Editable outputs",
        "outputs": ("Figures", "Presentations", "Papers"),
        "formats": ("ohmyplt", "Editable PowerPoint", "LaTeX source"),
    },
}


def get_font(chinese, bold=False):
    if chinese:
        filename = "msyhbd.ttc" if bold else "msyh.ttc"
        families = ("Microsoft YaHei", "Noto Sans CJK SC", "Noto Sans SC", "PingFang SC")
    else:
        filename = "arialbd.ttf" if bold else "arial.ttf"
        families = ("Arial", "Liberation Sans", "DejaVu Sans")
    font_path = WINDOWS_FONTS / filename
    if font_path.is_file():
        return FontProperties(fname=font_path)
    for family in families:
        properties = FontProperties(family=family, weight="bold" if bold else "normal")
        try:
            findfont(properties, fallback_to_default=False)
        except ValueError:
            continue
        return properties
    raise RuntimeError(f"Install one of these fonts: {', '.join(families)}")


def load_icons():
    icons = {}
    for name in (*TOOLS, "ohmyplt.png"):
        path = HERE / "tools" / name
        if path.suffix == ".svg":
            source = path.read_text(encoding="utf-8")
            if name == "obsidian.svg":
                # The original icon expects dimensions from its embedding page.
                source = source.replace('height="100%" width="100%"',
                                        'height="512" width="512"', 1)
            path = BytesIO(svg_to_bytes(svg_string=source, width=256, dpi=96))
        with Image.open(path) as image:
            icons[name] = image.convert("RGBA")
    return icons


def mm(x, y):
    return x / 6, (HEIGHT - y) / 6


class WorkflowPanel:
    """Draw in the original cover coordinates before cropping the diagram."""

    def __init__(self, plate, icons, language):
        self.icons = icons
        self.fonts = {
            "body": get_font(language == "zh"),
            "bold": get_font(language == "zh", bold=True),
            "tool": get_font(False, bold=True),
        }
        self.plate = plate(180, 240)
        self.figure, self.ax = self.plate.fig, self.plate.ax
        self.figure.set_facecolor(PAPER)
        x, y = mm(CROP[0], CROP[3])
        self.ax.add_patch(Rectangle(
            (x, y), WIDTH / 6, (CROP[3] - CROP[1]) / 6, facecolor=DARK,
            edgecolor="none", zorder=.5,
        ))

    def text(self, x, y, label, size, color=LIGHT, *, face="body", align="left"):
        return self.plate.text(
            *mm(x, y), label, size=size * 72 / DPI, color=color, ha=align,
            va="center", fontproperties=self.fonts[face],
        )

    def ring(self, x, y, radius, color, *, fill="none", lw=2, z=3):
        self.ax.add_patch(Circle(mm(x, y), radius / 6, edgecolor=color, facecolor=fill,
                                 lw=lw * 72 / DPI, zorder=z))

    def wire(self, *points, color=MINT, lw=2.5, radius=23, arrow=True):
        return self.plate.wire(
            [mm(x, y) for x, y in points], color=color, lw=lw * 72 / DPI,
            r=radius / 6, arrow=arrow, head=16 * 72 / DPI,
        )

    def port(self, x, y, field, *, vertical=True):
        slot = self.plate.port(*mm(x, y), vertical=vertical, width=1.4, gap=1.7)
        slot.set_facecolor(field)
        slot.set_zorder(2.15)
        self.ring(x, y, 4.1, MINT, fill=field, lw=1.8, z=4)

    def icon(self, name, x, y, size):
        image = self.icons[name]
        scale = size / max(image.size)
        width, height = (value * scale for value in image.size)
        left, bottom = mm(x - width / 2, y + height / 2)
        right, top = mm(x + width / 2, y - height / 2)
        self.ax.imshow(image, extent=(left, right, bottom, top), aspect="auto",
                       interpolation="lanczos", zorder=5)

    def output_mark(self, mark, x, y, size):
        if mark == "ohmyplt.png":
            self.icon(mark, x, y, size)
            return
        self.plate.card(
            *mm(x - size / 2, y + size / 2), size / 6, size / 6,
            face="#DAE9DB", edge="#DAE9DB", r=2.0,
        )
        edge = size * .32
        if mark == "slides":
            self.wire(
                (x - edge, y + 8), (x - edge, y - edge + 6), (x + edge, y - edge + 6),
                (x + edge, y + 8), (x - edge, y + 8), arrow=False, radius=2,
                color=DARK, lw=2,
            )
            self.wire((x, y + 8), (x, y + edge), arrow=False, color=DARK, lw=2)
            self.wire((x - 10, y + edge), (x + 10, y + edge), arrow=False, color=DARK, lw=2)
        else:
            self.wire(
                (x - 13, y - edge), (x + 6, y - edge), (x + 14, y - edge + 8),
                (x + 14, y + edge), (x - 13, y + edge), (x - 13, y - edge),
                arrow=False, radius=2, color=DARK, lw=2,
            )
            for offset in (-4, 4, 12):
                self.wire((x - 7, y + offset), (x + 8, y + offset),
                          arrow=False, color=DARK, lw=1.6)

    def save(self, destination):
        self.figure.set_dpi(DPI)
        self.figure.canvas.draw()
        renderer = self.figure.canvas.get_renderer()
        left, top, right, bottom = CROP
        for label in self.ax.texts:
            box = label.get_window_extent(renderer)
            if not (left < box.x0 and box.x1 < right and
                    HEIGHT - bottom < box.y0 and box.y1 < HEIGHT - top):
                raise ValueError(f"Label outside the diagram: {label.get_text()}")
        with BytesIO() as buffer:
            self.figure.savefig(buffer, format="png", dpi=DPI, facecolor=PAPER)
            buffer.seek(0)
            with Image.open(buffer) as full:
                if full.size != (WIDTH, HEIGHT):
                    raise ValueError(f"Unexpected canvas: {full.size}")
                full.crop(CROP).convert("RGB").save(destination, optimize=True)
        plt.close(self.figure)


def render(plate, language, icons):
    words = WORDS[language]
    diagram = WorkflowPanel(plate, icons, language)
    chinese = language == "zh"

    for x, title in zip((64, 774), words["headings"], strict=True):
        diagram.text(x, 498, title, 35 if chinese else 27, MINT, face="bold")
    positions = ((94, 610), (94, 777), (805, 610), (805, 777))
    for icon, name, description, (x, y) in zip(
        TOOLS, ("Obsidian", "Zotero", "Git", "Snakemake"), words["roles"], positions,
        strict=True,
    ):
        diagram.ring(x, y, 37, "#D7E3D6", fill="#F3F6EF", lw=1.2)
        diagram.icon(icon, x, y, 52)
        diagram.text(x + 51, y - 12, name, 30, face="tool")
        diagram.text(x + 51, y + 27, description, 20 if chinese else 18, MINT)

    diagram.ring(540, 690, 125, "#749987", fill=FILM, lw=3)
    diagram.ring(540, 690, 110, "#496F5D", lw=1.3)
    diagram.text(540, 670, words["home"], 46 if chinese else 34, align="center", face="bold")
    diagram.text(540, 731, words["home_detail"], 22 if chinese else 16, MINT, align="center")
    for first, bend, target in ((307, 355, 415), (760, 719, 665)):
        diagram.wire((first, 610), (bend, 610), (bend, 777), (first, 777), arrow=False, lw=1.9)
        diagram.wire((bend, 690), (target, 690), lw=2.7)
        diagram.port(first, 610, DARK, vertical=False)
        diagram.port(first, 777, DARK, vertical=False)
        diagram.port(target, 690, FILM, vertical=False)

    diagram.port(540, 815, DARK)
    diagram.wire((540, 815), (540, 910), arrow=False)
    outputs = diagram.text(540, 890, words["outputs_title"], 35, align="center", face="bold")
    outputs.set_bbox(dict(facecolor=DARK, edgecolor="none", pad=7))
    diagram.wire((540, 919), (540, 948), arrow=False)
    columns = (212, 540, 868)
    for x in columns:
        diagram.wire((540, 948), (x, 948), (x, 1009), lw=2.4)
        diagram.port(x, 1009, DARK)
    diagram.ring(540, 948, 4.5, MINT, fill=MINT, lw=1)
    for x, mark, title, format_ in zip(columns, OUTPUTS, words["outputs"], words["formats"], strict=True):
        diagram.output_mark(mark, x, 1064, 68)
        diagram.text(x, 1148, title, 37, align="center", face="bold")
        diagram.text(x, 1198, format_, 24, MINT, align="center")

    suffix = "" if chinese else ".en"
    diagram.save(HERE / f"research-workflow{suffix}.png")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--ohmyplt", type=Path, default=Path.home() / ".codex" / "skills" / "ohmyplt",
                        help="Path to the ohmyplt skill directory")
    args = parser.parse_args()
    scripts = args.ohmyplt / "scripts"
    if not (scripts / "ohmyplt.py").is_file():
        parser.error("Install ohmyplt or pass its skill directory with --ohmyplt.")
    sys.path.insert(0, str(scripts.resolve()))
    from ohmyplt import Plate, configure

    latin = get_font(False).get_name()
    configure(body_font=latin, math_font=latin, fallback_fonts=(get_font(True).get_name(),))
    asset_icons = load_icons()
    for lang in WORDS:
        render(Plate, lang, asset_icons)


if __name__ == "__main__":
    main()
