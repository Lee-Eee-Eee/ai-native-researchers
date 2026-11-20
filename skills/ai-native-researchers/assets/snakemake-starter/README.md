# From observations to a result you can reproduce

Copy this directory into a project and run the commands below from the copy. The example compares two synthetic time series. Which series reached its highest **observed** reading first, and how far did each move between its first and last valid readings?

## Run it

With Python 3.12 and [uv](https://docs.astral.sh/uv/), install Snakemake into a dedicated environment in the copied directory.

```sh
uv venv --python 3.12 .venv
uv pip install --python .venv snakemake==9.27.0
```

Activate it with `source .venv/bin/activate` in Bash or `.\.venv\Scripts\Activate.ps1` in PowerShell. If you already have an active environment with Snakemake 9.27.0, start here. Preview the jobs, run them, then repeat the run.

```sh
snakemake --cores 1 --dry-run
snakemake --cores 1
snakemake --cores 1
```

The repeat run should report `Nothing to be done`.

## Follow one observation

The input file `data/observations.csv` contains seven rows. Time is in hours and readings use arbitrary units. Series B has a blank reading at hour 1 and the same highest reading at hours 3 and 4. Rows can arrive out of order.

1. `check_observations` rejects duplicate series/time pairs, missing IDs, non-finite numbers, and series with no valid readings. It counts blank readings, skips those rows, and sorts the accepted observations by series and time. Open `results/quality.json` to see how many readings were used. Open `results/accepted.csv` to inspect them.
2. `summarize` reads the accepted observations and writes `results/summary.csv`. A tie goes to the first observed peak. Change means last valid reading minus first valid reading. A peak between observations can go undetected.

| Series | Valid readings | Peak | First peak (h) | Change |
| --- | ---: | ---: | ---: | ---: |
| A | 3 | 12.5 | 2 | +1 |
| B | 3 | 13 | 3 | +4 |

The quality report should show 7 rows read, 6 accepted, 1 missing reading, and 2 series. To check how a failure is handled, make a fresh copy of the example, append `A,0,70` to its input and run it. The first rule reports the duplicate A observation at hour 0 and stops before producing a summary.
