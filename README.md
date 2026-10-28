# Explainable Cyber Threat Defense Workbench

A focused, one-notebook benchmark of **open-world network-flow triage under a fixed review budget**. The experiment withholds one attack category from training at a time, then compares known-attack risk, normal-only novelty scoring, and a two-lane review queue on UNSW-NB15.

The central question is practical: **when a model has never seen one attack category, which ranking policy finds examples from it, and how much benign traffic enters the review queue?** The project measures that trade-off at 5%, 10%, and 20% review budgets. The 10% budget is the primary comparison.

## Start here

| File | Purpose |
| --- | --- |
| [docs/PROJECT_GUIDE.md](docs/PROJECT_GUIDE.md) | Research question, data fields, split, queue design, and metric definitions. |
| [cyber_threat_modeling.ipynb](cyber_threat_modeling.ipynb) | Full reproducible analysis, tables, charts, and a local model explanation. |
| [docs/FINDINGS.md](docs/FINDINGS.md) | Measured open-world results and limitations. |
| [docs/Cyber_Threat_Defense_Expert_Briefing.pdf](docs/Cyber_Threat_Defense_Expert_Briefing.pdf) | Slide-style briefing on the pattern history, experiment, results, and caveats. |

## What the benchmark compares

For each of nine leave-one-attack-category-out folds:

1. Withhold that category's labeled training rows and exact duplicate inputs.
2. Fit an XGBoost known-risk model on normal flows and the remaining attack categories.
3. Fit an Isolation Forest on normal flows only to rank behavioral novelty.
4. Rank the same primary test flows using three policies: **known-risk only**, **novelty only**, and a **75/25 two-lane queue** (75% known-risk, 25% novelty among flows not already selected).
5. Compare held-out-category recall, known-category recall, precision, and normal alerts per 1,000 normal flows at equal queue sizes.

The 75/25 allocation is a transparent design choice, not a claimed industry standard or an optimized result. This is a benchmark of an open-world evaluation and review policy, not a claim that the queue architecture is novel or ready for deployment.

## Set up

Use Python 3.11 or newer from the repository folder:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

In VS Code, open `cyber_threat_modeling.ipynb`, select `.venv/bin/python` as the kernel, and run the cells from top to bottom. The committed notebook contains an executed run, including the result tables and figures.

## Get the data

The [UNSW-NB15 research page](https://research.unsw.edu.au/projects/unsw-nb15-dataset) describes the dataset and published train/test split. Put these two files in `data/raw/`:

- `UNSW_NB15_training-set.csv` (175,341 flows)
- `UNSW_NB15_testing-set.csv` (82,332 flows)

The current university download may require Microsoft sign-in. The saved run used a [public mirror of the same named CSVs](https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/tree/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f):

```bash
mkdir -p data/raw
curl -L --fail -o data/raw/UNSW_NB15_training-set.csv 'https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/resolve/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f/UNSW_NB15_training-set.csv'
curl -L --fail -o data/raw/UNSW_NB15_testing-set.csv 'https://huggingface.co/datasets/Mouwiya/UNSW-NB15-small/resolve/6f5f54594dfc80c84264aec4c7cc3d9b162f1e2f/UNSW_NB15_testing-set.csv'
```

The notebook records file hashes. Raw CSVs are excluded from Git.

## Data and selected columns

Each row is a network connection flow. The model uses 20 columns:

- **Traffic measurements (12):** `dur`, `spkts`, `dpkts`, `sbytes`, `dbytes`, `rate`, `sttl`, `dttl`, `sload`, `dload`, `sloss`, `dloss` describe duration, packet and byte counts, rates, time-to-live values, and packet loss.
- **Recent connection counts (5):** `ct_srv_src`, `ct_dst_ltm`, `ct_src_dport_ltm`, `ct_dst_sport_ltm`, `ct_dst_src_ltm` summarize activity involving services, hosts, and ports.
- **Connection categories (3):** `proto`, `service`, and `state` identify protocol, service, and connection state.

`label` is the binary normal/attack target. `attack_cat` is used only to create held-out folds and report category-level results. `id` is a row identifier. None of these three fields is a model input. The Isolation Forest uses eight numeric traffic measurements and is fit only on normal-labeled training flows.

## Scope and interpretation

“Unseen attack” means **a labeled UNSW-NB15 attack category withheld from model training**. It is a controlled proxy for unknown behavior, not evidence of zero-day detection. The dataset has no timestamps, so this does not evaluate future-period drift. Exact input matches between the published training and test files are removed from the primary test population; that cannot remove every relationship among flows.

UNSW-NB15 is a cyber-range dataset with a high attack-label share. Precision and benign-alert rates here are specific to this benchmark and should not be read as estimates for a live network. The open-world and unknown-class problem is an active research area; this project makes a bounded, reproducible comparison rather than claiming a new detection algorithm.
