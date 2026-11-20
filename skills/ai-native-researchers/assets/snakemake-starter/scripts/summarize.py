import csv
from itertools import groupby
from operator import itemgetter


def summarize(source, destination):
    with open(source, newline="", encoding="utf-8") as src, open(
        destination, "w", newline="", encoding="utf-8"
    ) as dest:
        rows = csv.DictReader(src)
        writer = csv.writer(dest, lineterminator="\n")
        writer.writerow(["series", "n", "peak_reading", "first_peak_h", "change"])
        for series, group in groupby(rows, key=itemgetter("series")):
            # The upstream rule has sorted the accepted readings by time.
            readings = [(float(row["time_h"]), float(row["reading"])) for row in group]
            peak_h, peak = max(readings, key=itemgetter(1))
            change = readings[-1][1] - readings[0][1]
            writer.writerow([series, len(readings), peak, peak_h, change])


summarize(snakemake.input[0], snakemake.output[0])
