"""Render the README figure from the runnable synthetic observation example."""

import argparse
import csv
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from matplotlib.ticker import MultipleLocator
import numpy as np


HERE = Path(__file__).resolve().parent
STARTER = HERE.parents[1] / "skills/ai-native-researchers/assets/snakemake-starter"
PAPER = "#F8F7F2"
WHITE = "#FFFFFF"
INK = "#19312E"
MUTED = "#4F645F"
EDGE = "#D6DDD5"
GREEN = "#226557"
CLAY = "#A04631"
TRANSLATIONS = {
    "zh": {
        "example": "合成数据示例",
        "question": "哪组观测最早达到本组最高读数？",
        "units": "读数（任意单位）",
        "time": "观测时刻（小时）",
        "missing": "{series} 缺测",
        "finding_label": "实验判断",
        "finding": "{first} 组早 {lead:g} 小时达到峰值",
        "peak_times": "{first}：{first_h:g} 小时　　{following}：{following_h:g} 小时",
        "evidence": "逐例证据",
        "quality": "{rows_read} 条记录中，{rows_accepted} 条有效，{missing_readings} 条缺测。",
        "rule": "并列最高读数取首次出现的时刻。",
        "workflow": ("输入", "复算", "输出"),
    },
    "en": {
        "example": "Synthetic-data example",
        "question": "Which series reaches its observed peak first?",
        "units": "Reading (arbitrary units)",
        "time": "Observation time (hours)",
        "missing": "{series} missing",
        "finding_label": "Finding",
        "finding": "{first} peaks {lead:g} hour earlier",
        "peak_times": "{first}: {first_h:g} h       {following}: {following_h:g} h",
        "evidence": "Evidence",
        "quality": "{rows_read} records  ·  {rows_accepted} valid  ·  {missing_readings} missing",
        "rule": "For ties, take the earliest observation.",
        "workflow": ("Input", "Rerun", "Output"),
    },
}


def chinese_font(path):
    if path:
        font = FontProperties(fname=path)
        font.get_name()
        return font.get_family(), font
    for name in ("Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "WenQuanYi Zen Hei"):
        try:
            findfont(FontProperties(family=name), fallback_to_default=False)
        except ValueError:
            continue
        return name, FontProperties(family=name)
    raise SystemExit("Install a Chinese font, or pass its file with --font.")


def run_example():
    """Use the same CSV quality checks and summaries as the Snakemake rules."""
    source = STARTER / "data/observations.csv"
    with source.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    with TemporaryDirectory() as temporary:
        accepted, report, summary = (Path(temporary) / name for name in ("accepted.csv", "quality.json", "summary.csv"))
        runpy.run_path(str(STARTER / "scripts/check_observations.py"), init_globals={
            "snakemake": SimpleNamespace(input=[str(source)], output=SimpleNamespace(
                observations=str(accepted), report=str(report)))})
        runpy.run_path(str(STARTER / "scripts/summarize.py"), init_globals={
            "snakemake": SimpleNamespace(input=[str(accepted)], output=[str(summary)])})
        quality = json.loads(report.read_text(encoding="utf-8"))
        with summary.open(encoding="utf-8", newline="") as stream:
            peaks = {row["series"]: (float(row["first_peak_h"]), float(row["peak_reading"]))
                     for row in csv.DictReader(stream)}
    return rows, quality, peaks


def create_figure(destination, font_path, language):
    copy = TRANSLATIONS[language]
    latin = FontProperties(family="Arial")
    family, body = chinese_font(font_path) if language == "zh" else ("Arial", latin)
    digits = FontProperties(family="Times New Roman", weight="bold")
    mono = FontProperties(family=["Consolas", "DejaVu Sans Mono"])
    title = FontProperties(family=family, fname=font_path if language == "zh" else None, weight="bold")
    records, quality, peaks = run_example()
    colors = dict(zip(peaks, (GREEN, CLAY), strict=True))
    ranking = sorted(peaks, key=lambda key: peaks[key][0])
    first, following = ranking
    lead = peaks[following][0] - peaks[first][0]

    fig = plt.figure(figsize=(12.5, 5.72), facecolor=PAPER)
    canvas = fig.add_axes([0, 0, 1, 1], zorder=0)
    canvas.set_xlim(0, 1)
    canvas.set_ylim(0, 1)
    canvas.axis("off")
    canvas.add_patch(FancyBboxPatch((.041, .132), .918, .609, boxstyle="round,pad=0.0,rounding_size=.018",
                                    facecolor=WHITE, edgecolor=EDGE, linewidth=.75))
    canvas.plot([.554, .554], [.174, .699], color=EDGE, linewidth=.8)

    def label(x, y, content, size, font=body, color=INK, **options):
        fig.text(x, y, content, fontproperties=font, fontsize=size, color=color,
                 va="center", **options)

    label(.050, .925, copy["example"], 12, title, GREEN)
    label(.049, .823, copy["question"], 29, title)
    label(.070, .674, copy["units"], 11, color=MUTED)

    chart = fig.add_axes([.095, .233, .419, .384], facecolor=WHITE, zorder=1)
    chart.set_axisbelow(True)
    chart.set_xlim(-.10, 4.20)
    readings = [float(row["reading"]) for row in records if row["reading"]]
    chart.set_ylim(min(readings)-.60, max(readings)+.65)
    chart.set_xticks(range(5))
    chart.yaxis.set_major_locator(MultipleLocator(1))
    chart.tick_params(axis="both", colors=MUTED, labelsize=10, length=0, pad=6)
    chart.grid(axis="y", color="#E6EAE6", linewidth=.75)
    chart.spines[["top", "right", "left"]].set_visible(False)
    chart.spines["bottom"].set_color(EDGE)
    for tick in chart.get_xticklabels() + chart.get_yticklabels():
        tick.set_fontproperties(latin)
        tick.set_fontsize(10)
    chart.set_xlabel(copy["time"], fontproperties=body, fontsize=11, labelpad=6, color=MUTED)
    for name, (peak_time, peak_value) in peaks.items():
        points = sorted((float(row["time_h"]), float(row["reading"]) if row["reading"] else np.nan)
                        for row in records if row["series"] == name)
        times, values = zip(*points)
        chart.plot(times, values, "o-", color=colors[name], linewidth=1.75, markersize=5, zorder=3)
        chart.scatter(peak_time, peak_value, color=colors[name], s=100, alpha=.21, linewidth=0, zorder=2)
        chart.annotate(f"{name}   {peak_value:g}", (peak_time, peak_value), xytext=(0, 10),
                       textcoords="offset points", ha="center", va="bottom", fontproperties=digits,
                       fontsize=12, color=colors[name])
    for row in records:
        if not row["reading"]:
            missing_x = float(row["time_h"])
            chart.text(missing_x, min(readings)+.36, copy["missing"].format(series=row["series"]), ha="center",
                       fontproperties=body, fontsize=10, color=MUTED,
                       bbox={"facecolor": WHITE, "edgecolor": "none", "pad": 1})

    label(.583, .674, "001", 12, digits, GREEN)
    label(.638, .674, copy["finding_label"], 13, title)
    label(.583, .568, copy["finding"].format(first=first, lead=lead), 19, title)
    label(.583, .498, copy["peak_times"].format(first=first, first_h=peaks[first][0],
          following=following, following_h=peaks[following][0]), 12, color=MUTED)
    canvas.plot([.582, .924], [.452, .452], color=EDGE, linewidth=.8)
    label(.583, .399, "001a", 12, digits, CLAY)
    label(.638, .399, copy["evidence"], 13, title)
    label(.583, .306, copy["quality"].format(**quality), 13)
    label(.583, .232, copy["rule"], 12, color=MUTED)

    for start, head, filename in zip((.050, .361, .713), copy["workflow"],
                                     ("observations.csv", "snakemake --cores 1", "summary.csv"), strict=True):
        label(start, .067, head, 10.5, title, MUTED)
        label(start+.054, .067, filename, 10.5, mono)
    for start, end in ((.275, .329), (.630, .681)):
        canvas.add_patch(FancyArrowPatch((start, .067), (end, .067), arrowstyle="-|>",
                                         mutation_scale=11, color=MUTED, linewidth=.95))

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    for element in fig.texts:
        bounds = element.get_window_extent(renderer)
        if not (fig.bbox.contains(bounds.x0, bounds.y0) and fig.bbox.contains(bounds.x1, bounds.y1)):
            raise ValueError(f"Label outside the canvas: {element.get_text()}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=144, facecolor=PAPER)
    plt.close(fig)
    print(f"{destination} | {quality} | peak time and value: {peaks}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--language", choices=("zh", "en"), default="zh")
    parser.add_argument("--output", type=Path, help="output path for the chosen language")
    parser.add_argument("--font", help="optional path to a Chinese font file")
    args = parser.parse_args()
    default_name = "research-demo.en.png" if args.language == "en" else "research-demo.png"
    create_figure(args.output or HERE / default_name, args.font, args.language)
