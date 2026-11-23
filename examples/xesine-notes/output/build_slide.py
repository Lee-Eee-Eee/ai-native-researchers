"""Build an editable slide describing the XeSINE-Net example project layout."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parent
DEEP = RGBColor.from_string("182B29")
ACCENT = RGBColor.from_string("2B695A")
MUTED = RGBColor.from_string("53625C")


def label(slide, left, top, width, height, content, size, color, bold=False):
    shape = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    run = shape.text_frame.paragraphs[0].add_run()
    run.text = content
    run.font.name = "Microsoft YaHei"
    run.font.size = Pt(size)
    run.font.color.rgb = color
    run.font.bold = bold


presentation = Presentation()
presentation.slide_width = Inches(13.333)
presentation.slide_height = Inches(7.5)
slide = presentation.slides.add_slide(presentation.slide_layouts[6])
label(slide, 0.6, 0.42, 11.9, 0.65, "XeSINE-Net · 项目组织", 30, DEEP, True)
label(slide, 0.6, 1.16, 7.1, 0.45, "阶段记录与交付文件", 18, ACCENT, True)
for y, heading, description in [
    (2.03, "项目首页", "当前研究接力、文献与进展、下一步"),
    (3.30, "阶段记录", "142—156 各有判断页和同号证据页"),
    (4.57, "研究交付", "绘图、汇报、论文由阶段页指向所用资料"),
]:
    label(slide, 0.6, y, 6.0, 0.45, heading, 20, DEEP, True)
    label(slide, 0.6, y + 0.47, 6.3, 0.5, description, 16, MUTED)
slide.shapes.add_picture(str(ROOT.parent / "previews/workflow.png"), Inches(7.25), Inches(0.97), height=Inches(6.15))
label(slide, 0.6, 6.84, 6.5, 0.25, "AI-Native Researchers · 项目结构示例", 10, MUTED)
presentation.save(ROOT / "项目组织示例.pptx")
